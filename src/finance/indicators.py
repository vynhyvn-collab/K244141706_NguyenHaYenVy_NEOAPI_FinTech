"""
Module tính toán các chỉ báo tài chính vi cấu trúc và kỹ thuật:
1. Độ lệch Cung - Cầu sổ lệnh (Order Book Imbalance - OBI) từ 3 bước giá tốt nhất (Top 3 Bids & Asks).
2. Thanh khoản phiên từ giá trị giao dịch NeoAPI.
3. Động lượng giá (Price Momentum): Biến động trong ngày và vị thế trong biên độ High-Low.
4. Dòng tiền ròng khối ngoại (Foreign Net Flow & Foreign Participation Rate).
"""
from typing import Dict, Any, Optional
from src.neo_api.models import StockSnapshot, StockOrderBook


class FinancialIndicatorCalculator:
    """Bộ tính toán chỉ báo tài chính và vi cấu trúc thị trường."""

    @staticmethod
    def calculate_order_book_imbalance(order_book: Optional[StockOrderBook]) -> Optional[float]:
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
            return None

        total_bid_vol = sum(b.volume for b in order_book.bids)
        total_ask_vol = sum(a.volume for a in order_book.asks)
        total_vol = total_bid_vol + total_ask_vol

        if total_vol == 0:
            return None

        obi = (total_bid_vol - total_ask_vol) / total_vol
        return round(float(obi), 4)

    @staticmethod
    def calculate_price_momentum(snapshot: StockSnapshot) -> Dict[str, Optional[float]]:
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

        if high > low and last > 0:
            range_pos = (last - low) / (high - low)
        else:
            range_pos = None

        return {
            "pct_change": round(pct_change, 2) if pct_change is not None else None,
            "range_position": round(range_pos, 4) if range_pos is not None else None
        }

    @staticmethod
    def calculate_foreign_metrics(snapshot: StockSnapshot) -> Dict[str, Optional[float]]:
        """
        Tính toán các thước đo dòng tiền khối ngoại:
        1. net_value: Giá trị mua/bán ròng (VNĐ).
        2. participation_rate: Tỷ lệ giao dịch khối ngoại trên tổng thanh khoản thị trường:
           PartRate = (ForeignBuyVal + ForeignSellVal) / TotalValue
        3. net_impact: Tỷ lệ mua ròng trên tổng thanh khoản:
           NetImpact = NetForeignVal / TotalValue
        """
        ft = snapshot.foreign_trade
        if not ft or ft.net_value is None or snapshot.total_value <= 0:
            return {
                "net_value": ft.net_value if ft else None,
                "participation_rate": None,
                "net_impact": None
            }

        if ft.buy_value is None or ft.sell_value is None:
            return {"net_value": ft.net_value, "participation_rate": None, "net_impact": None}
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
        mom = cls.calculate_price_momentum(snapshot)
        foreign = cls.calculate_foreign_metrics(snapshot)

        return {
            "symbol": snapshot.symbol,
            "timestamp": snapshot.timestamp,
            "last_price": snapshot.last_price,
            "order_book_imbalance": obi,
            "pct_change": mom["pct_change"],
            "range_position": mom["range_position"],
            "foreign_net_value": foreign["net_value"],
            "foreign_net_impact": foreign["net_impact"],
            "total_value": snapshot.total_value
        }
