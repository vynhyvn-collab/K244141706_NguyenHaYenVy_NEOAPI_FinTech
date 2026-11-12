"""
Module tính toán các chỉ báo tài chính vi cấu trúc và kỹ thuật:
1. Độ lệch Cung - Cầu sổ lệnh (Order Book Imbalance - OBI) từ 3 bước giá tốt nhất (Top 3 Bids & Asks).
2. Đột biến khối lượng (Relative Volume - RelVol = Vol / MA20_Vol) và Mức độ thanh khoản.
3. Động lượng giá (Price Momentum): Biến động trong ngày và vị thế trong biên độ High-Low.
4. Dòng tiền ròng khối ngoại (Foreign Net Flow & Foreign Participation Rate).
"""
from typing import Dict, Any
from src.neo_api.models import StockSnapshot, StockOrderBook


class FinancialIndicatorCalculator:
    """Bộ tính toán chỉ báo tài chính và vi cấu trúc thị trường."""

    @staticmethod
    def calculate_order_book_imbalance(order_book: StockOrderBook) -> float:
        """
        Tính toán Độ lệch Cung - Cầu sổ lệnh (Order Book Imbalance - OBI).
        Công thức:
            OBI = (Tổng BidVol_1..3 - Tổng AskVol_1..3) / (Tổng BidVol_1..3 + Tổng AskVol_1..3)
        Giá trị:
            Thuộc khoảng [-1.0, 1.0].
            > 0: Lực Cầu (Mua) áp đảo lực Cung (Bán) -> Áp lực đẩy giá tăng ngắn hạn.
            < 0: Lực Cung (Bán) áp đảo lực Cầu (Mua) -> Áp lực giảm giá ngắn hạn.
        """
        if not order_book or not order_book.bids or not order_book.asks:
            return 0.0

        total_bid_vol = sum(b.volume for b in order_book.bids)
        total_ask_vol = sum(a.volume for a in order_book.asks)
        total_vol = total_bid_vol + total_ask_vol

        if total_vol == 0:
            return 0.0

        obi = (total_bid_vol - total_ask_vol) / total_vol
        return round(float(obi), 4)

    @staticmethod
    def calculate_relative_volume(snapshot: StockSnapshot) -> float:
        """
        Tính Đột biến khối lượng (Relative Volume - RelVol).
        Công thức:
            RelVol = TotalVolume / AvgVolume20d
        Ý nghĩa:
            > 1.5: Khối lượng giao dịch đột biến gấp 1.5 lần mức trung bình.
        """
        avg_vol = snapshot.avg_volume_20d
        if avg_vol <= 0:
            return 1.0
        return round(float(snapshot.total_volume / avg_vol), 2)

    @staticmethod
    def calculate_price_momentum(snapshot: StockSnapshot) -> Dict[str, float]:
        """
        Tính Động lượng giá (Price Momentum):
        1. pct_change: % thay đổi giá so với tham chiếu.
        2. range_position: Vị thế giá hiện tại trong biên độ (High - Low) trong ngày:
           Position = (Last - Low) / (High - Low)
           Gần 1.0: Đóng cửa/Giao dịch ở mức cao nhất ngày (lực mua duy trì mạnh đến cuối).
        """
        pct_change = snapshot.pct_change
        high = snapshot.high_price
        low = snapshot.low_price
        last = snapshot.last_price

        if high > low:
            range_pos = (last - low) / (high - low)
        else:
            range_pos = 0.5

        return {
            "pct_change": round(pct_change, 2),
            "range_position": round(range_pos, 4)
        }

    @staticmethod
    def calculate_foreign_metrics(snapshot: StockSnapshot) -> Dict[str, float]:
        """
        Tính toán các thước đo dòng tiền khối ngoại:
        1. net_value: Giá trị mua/bán ròng (VNĐ).
        2. participation_rate: Tỷ lệ giao dịch khối ngoại trên tổng thanh khoản thị trường:
           PartRate = (ForeignBuyVal + ForeignSellVal) / TotalValue
        3. net_impact: Tỷ lệ mua ròng trên tổng thanh khoản:
           NetImpact = NetForeignVal / TotalValue
        """
        ft = snapshot.foreign_trade
        if not ft or snapshot.total_value <= 0:
            return {
                "net_value": 0.0,
                "participation_rate": 0.0,
                "net_impact": 0.0
            }

        total_foreign_val = ft.buy_value + ft.sell_value
        part_rate = total_foreign_val / snapshot.total_value if snapshot.total_value > 0 else 0.0
        net_impact = ft.net_value / snapshot.total_value if snapshot.total_value > 0 else 0.0

        return {
            "net_value": round(ft.net_value, 2),
            "participation_rate": round(part_rate, 4),
            "net_impact": round(net_impact, 4)
        }

    @classmethod
    def compute_all_metrics(cls, snapshot: StockSnapshot) -> Dict[str, Any]:
        """Tổng hợp toàn bộ các chỉ số vi cấu trúc của 1 cổ phiếu."""
        obi = cls.calculate_order_book_imbalance(snapshot.order_book)
        rel_vol = cls.calculate_relative_volume(snapshot)
        mom = cls.calculate_price_momentum(snapshot)
        foreign = cls.calculate_foreign_metrics(snapshot)

        return {
            "symbol": snapshot.symbol,
            "timestamp": snapshot.timestamp,
            "last_price": snapshot.last_price,
            "order_book_imbalance": obi,
            "relative_volume": rel_vol,
            "pct_change": mom["pct_change"],
            "range_position": mom["range_position"],
            "foreign_net_value": foreign["net_value"],
            "foreign_net_impact": foreign["net_impact"],
            "total_value": snapshot.total_value
        }
