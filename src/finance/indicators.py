"""
Module tính toán các chỉ báo tài chính vi cấu trúc và kỹ thuật:
1. Độ lệch Cung - Cầu sổ lệnh (Order Book Imbalance - OBI) có trọng số theo khoảng cách bước giá:
   - Bước 1 (sát giá khớp nhất): Trọng số 50%
   - Bước 2: Trọng số 30%
   - Bước 3: Trọng số 20%
2. Giá bình quân gia quyền theo khối lượng (VWAP) và Tỷ lệ chênh lệch giá so với VWAP.
3. Độ rộng chênh lệch Mua - Bán (Bid-Ask Spread).
4. Đột biến khối lượng (Relative Volume - RelVol = Vol / MA20_Vol).
5. Động lượng giá (Price Momentum): Biến động trong ngày và vị thế trong biên độ High-Low.
6. Dòng tiền ròng của khối ngoại (Foreign Net Flow & Foreign Participation Rate).
"""
from typing import Dict, Any, Optional
from src.neo_api.models import StockSnapshot, StockOrderBook


class FinancialIndicatorCalculator:
    """Bộ tính toán chỉ báo tài chính và vi cấu trúc thị trường chứng khoán."""

    @staticmethod
    def calculate_order_book_imbalance(order_book: Optional[StockOrderBook]) -> float:
        """
        Tính toán Độ lệch Cung - Cầu sổ lệnh (OBI) có trọng số theo độ sâu bước giá:
            w1 = 0.5 (Bước 1), w2 = 0.3 (Bước 2), w3 = 0.2 (Bước 3).
        Công thức:
            WeightedBid = w1*BidVol1 + w2*BidVol2 + w3*BidVol3
            WeightedAsk = w1*AskVol1 + w2*AskVol2 + w3*AskVol3
            OBI = (WeightedBid - WeightedAsk) / (WeightedBid + WeightedAsk)
        Giá trị:
            Thuộc khoảng [-1.0, 1.0].
            > 0: Lực Cầu (Mua) áp đảo lực Cung (Bán) -> Áp lực đẩy giá tăng ngắn hạn.
            < 0: Lực Cung (Bán) áp đảo lực Cầu (Mua) -> Áp lực giảm giá ngắn hạn.
        """
        if not order_book or not order_book.bids or not order_book.asks:
            return 0.0

        weights = [0.5, 0.3, 0.2]

        weighted_bid = sum(
            w * b.volume for w, b in zip(weights, order_book.bids) if b.volume > 0
        )
        weighted_ask = sum(
            w * a.volume for w, a in zip(weights, order_book.asks) if a.volume > 0
        )
        total_vol = weighted_bid + weighted_ask

        if total_vol <= 0:
            return 0.0

        obi = (weighted_bid - weighted_ask) / total_vol
        return round(float(obi), 4)

    @staticmethod
    def calculate_bid_ask_spread(order_book: Optional[StockOrderBook], last_price: float) -> Dict[str, float]:
        """
        Tính độ rộng chênh lệch Mua - Bán tốt nhất (Bid-Ask Spread):
            Spread = Ask1_Price - Bid1_Price
            SpreadPct = Spread / LastPrice
        Spread càng hẹp thì thanh khoản tức thời càng dồi dào, rủi ro trượt giá càng thấp.
        """
        if not order_book or not order_book.bids or not order_book.asks:
            return {"spread": 0.0, "spread_pct": 0.0}

        bid1 = order_book.bids[0].price
        ask1 = order_book.asks[0].price

        if bid1 <= 0 or ask1 <= 0 or ask1 < bid1:
            return {"spread": 0.0, "spread_pct": 0.0}

        spread = ask1 - bid1
        spread_pct = (spread / last_price * 100.0) if last_price > 0 else 0.0

        return {
            "spread": round(spread, 1),
            "spread_pct": round(spread_pct, 3)
        }

    @staticmethod
    def calculate_vwap_metric(snapshot: StockSnapshot) -> Dict[str, float]:
        """
        Ước tính Giá bình quân gia quyền theo khối lượng (VWAP) trong ngày:
            VWAP = Tổng Giá Trị Khớp / Tổng Khối Lượng Khớp
            VWAP_Bias = (LastPrice - VWAP) / VWAP
        Nếu giá hiện tại nằm trên VWAP (Bias > 0), phe mua đang chấp nhận trả giá cao hơn trung bình.
        """
        if snapshot.total_volume <= 0 or snapshot.total_value <= 0:
            return {"vwap": snapshot.last_price, "vwap_bias": 0.0}

        vwap = snapshot.total_value / snapshot.total_volume
        bias = ((snapshot.last_price - vwap) / vwap * 100.0) if vwap > 0 else 0.0

        return {
            "vwap": round(vwap, 1),
            "vwap_bias": round(bias, 2)
        }

    @staticmethod
    def calculate_relative_volume(snapshot: StockSnapshot) -> float:
        """
        Tính Đột biến khối lượng (Relative Volume - RelVol).
        Công thức:
            RelVol = TotalVolume / AvgVolume20d
        Ý nghĩa:
            > 1.2: Khối lượng giao dịch tăng đột biến so với mức trung bình.
        """
        avg_vol = snapshot.avg_volume_20d
        if avg_vol <= 0:
            return 1.0
        return round(float(snapshot.total_volume / avg_vol), 2)

    @staticmethod
    def calculate_price_momentum(snapshot: StockSnapshot) -> Dict[str, float]:
        """
        Tính Động lượng giá:
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
        Tính toán các thước đo dòng tiền của khối ngoại:
        1. net_value: Giá trị mua/bán ròng (VNĐ).
        2. participation_rate: Tỷ lệ giao dịch khối ngoại trên tổng thanh khoản thị trường.
        3. net_impact: Tỷ lệ mua ròng trên tổng thanh khoản.
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
        """Tổng hợp toàn bộ các chỉ số vi cấu trúc thực tế của 1 cổ phiếu."""
        obi = cls.calculate_order_book_imbalance(snapshot.order_book)
        spread_info = cls.calculate_bid_ask_spread(snapshot.order_book, snapshot.last_price)
        vwap_info = cls.calculate_vwap_metric(snapshot)
        rel_vol = cls.calculate_relative_volume(snapshot)
        mom = cls.calculate_price_momentum(snapshot)
        foreign = cls.calculate_foreign_metrics(snapshot)

        return {
            "symbol": snapshot.symbol,
            "timestamp": snapshot.timestamp,
            "last_price": snapshot.last_price,
            "order_book_imbalance": obi,
            "spread": spread_info["spread"],
            "spread_pct": spread_info["spread_pct"],
            "vwap": vwap_info["vwap"],
            "vwap_bias": vwap_info["vwap_bias"],
            "relative_volume": rel_vol,
            "pct_change": mom["pct_change"],
            "range_position": mom["range_position"],
            "foreign_net_value": foreign["net_value"],
            "foreign_net_impact": foreign["net_impact"],
            "total_value": snapshot.total_value,
            "total_volume": snapshot.total_volume,
            "exchange": snapshot.exchange
        }
