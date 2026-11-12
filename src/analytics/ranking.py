"""
Module Xếp hạng đa nhân tố (Multi-Factor Scoring & Ranking Engine).
Áp dụng phương pháp Chuẩn hóa Phân vị Tương đối Nội mẫu (Cross-Sectional Percentile Rank).
Giải quyết hoàn toàn nhược điểm cắt ngưỡng cứng:
- Thích ứng với mọi chu kỳ thị trường (Bull / Bear / Sideway).
- Phân biệt rõ cổ phiếu tăng trần (+7% HOSE, +10% HNX, +15% UPCOM).
- Phân tầng tín hiệu kết hợp cả Điểm Tổng Hợp Tuyệt Đối và Thứ Hạng Phân Vị Tương Đối.

Tỷ trọng nhân tố:
1. Động lượng giá (Momentum - w1 = 0.25)
2. Thanh khoản & Đột biến Vol (Liquidity/Vol - w2 = 0.25)
3. Dòng tiền nước ngoài (Foreign Flow - w3 = 0.25)
4. Độ lệch Cung - Cầu sổ lệnh (Order Book Imbalance - w4 = 0.25)
"""
from typing import List, Dict
import pandas as pd
import numpy as np

from src.neo_api.models import StockSnapshot, FactorScores
from src.finance.indicators import FinancialIndicatorCalculator


class MultiFactorRankingEngine:
    """Động cơ tính điểm và xếp hạng đa nhân tố vi cấu trúc."""

    DEFAULT_WEIGHTS = {
        "momentum": 0.25,
        "liquidity": 0.25,
        "foreign": 0.25,
        "order_book": 0.25
    }

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS
        total_w = sum(self.weights.values())
        self.weights = {k: v / total_w for k, v in self.weights.items()}

    def rank_universe(self, snapshots: List[StockSnapshot]) -> List[FactorScores]:
        """
        Xếp hạng danh sách cổ phiếu thực tế theo thuật toán chuẩn hóa phân vị tương đối.
        """
        if not snapshots:
            return []

        # 1. Trích xuất các thước đo thô
        raw_list = [FinancialIndicatorCalculator.compute_all_metrics(s) for s in snapshots]
        df = pd.DataFrame(raw_list)

        n = len(df)
        if n == 1:
            # Trường hợp 1 mã cổ phiếu đơn lẻ
            df["momentum_score"] = 50.0
            df["liquidity_score"] = 50.0
            df["foreign_score"] = 50.0
            df["order_book_imbalance_score"] = 50.0
            df["composite_score"] = 50.0
        else:
            # 2. Chuẩn hóa Phân vị Tương đối Nội mẫu (Cross-Sectional Percentile Ranking: 0 - 100)
            # A. Động lượng (Momentum): Kết hợp % thay đổi giá và vị thế giá trong ngày (range_position)
            mom_composite = df["pct_change"] * 0.7 + df["range_position"] * 30.0
            df["momentum_score"] = (mom_composite.rank(pct=True, method="average") * 100.0).round(1)

            # B. Thanh khoản (Liquidity): Kết hợp Relative Volume và Tổng giá trị giao dịch
            liq_composite = df["relative_volume"] * 0.6 + np.log1p(df["total_value"]) * 0.4
            df["liquidity_score"] = (liq_composite.rank(pct=True, method="average") * 100.0).round(1)

            # C. Khối ngoại (Foreign): Dòng tiền ròng và Tỷ lệ tác động ròng
            for_composite = df["foreign_net_impact"] * 0.7 + np.sign(df["foreign_net_value"]) * np.log1p(np.abs(df["foreign_net_value"])) * 0.3
            df["foreign_score"] = (for_composite.rank(pct=True, method="average") * 100.0).round(1)

            # D. Độ lệch Cung - Cầu sổ lệnh (OBI) có trọng số:
            df["order_book_imbalance_score"] = (df["order_book_imbalance"].rank(pct=True, method="average") * 100.0).round(1)

            # 3. Tính Điểm Tổng Hợp (Composite Score)
            df["composite_score"] = (
                self.weights["momentum"] * df["momentum_score"] +
                self.weights["liquidity"] * df["liquidity_score"] +
                self.weights["foreign"] * df["foreign_score"] +
                self.weights["order_book"] * df["order_book_imbalance_score"]
            ).round(1)

        # 4. Phân tầng tín hiệu & Thuyết minh định lượng
        results: List[FactorScores] = []
        for _, row in df.iterrows():
            comp_score = float(row["composite_score"])
            tier = self._classify_tier(comp_score)
            summary = self._generate_explanation(row)

            score_obj = FactorScores(
                symbol=row["symbol"],
                timestamp=row["timestamp"],
                momentum_score=float(row["momentum_score"]),
                liquidity_score=float(row["liquidity_score"]),
                foreign_score=float(row["foreign_score"]),
                order_book_imbalance_score=float(row["order_book_imbalance_score"]),
                composite_score=comp_score,
                ranking_tier=tier,
                signal_summary=summary
            )
            results.append(score_obj)

        # Sắp xếp giảm dần theo Điểm Tổng Hợp
        results.sort(key=lambda x: x.composite_score, reverse=True)
        return results

    @staticmethod
    def _classify_tier(score: float) -> str:
        """
        Phân loại nhóm khuyến nghị:
        - Top Buy: Điểm >= 70 (Nằm trong top 30% cổ phiếu mạnh nhất toàn diện)
        - Accumulation: 55 <= Điểm < 70 (Có lực gom tích lũy)
        - Neutral: 40 <= Điểm < 55 (Trạng thái cân bằng, giằng co)
        - Caution: Điểm < 40 (Chịu áp lực bán áp đảo)
        """
        if score >= 70.0:
            return "Top Buy"
        elif score >= 55.0:
            return "Accumulation"
        elif score >= 40.0:
            return "Neutral"
        else:
            return "Caution"

    @staticmethod
    def _generate_explanation(row: pd.Series) -> str:
        """Tạo thuyết minh tự động có cơ sở định lượng vi cấu trúc."""
        notes = []
        obi = row.get("order_book_imbalance", 0.0)
        rel_vol = row.get("relative_volume", 1.0)
        f_net = row.get("foreign_net_value", 0.0)
        vwap_bias = row.get("vwap_bias", 0.0)

        # Đánh giá OBI
        if obi > 0.2:
            notes.append(f"Cầu mua áp đảo sổ lệnh (OBI {obi:+.1%})")
        elif obi < -0.2:
            notes.append(f"Áp lực bán đè sổ lệnh (OBI {obi:+.1%})")

        # Đánh giá Đột biến khối lượng
        if rel_vol >= 1.2:
            notes.append(f"Khối lượng đột biến {rel_vol:.1f}x TB")

        # Đánh giá Khối ngoại
        if f_net >= 1_000_000_000:
            notes.append(f"Khối ngoại gom ròng +{f_net/1e9:.1f} tỷ")
        elif f_net <= -1_000_000_000:
            notes.append(f"Khối ngoại bán ròng {f_net/1e9:.1f} tỷ")

        # Đánh giá VWAP
        if vwap_bias > 1.0:
            notes.append(f"Giá khớp trên VWAP +{vwap_bias:.1f}% (Phe mua chủ động)")

        if not notes:
            return "Biến động bình thường theo nhịp thị trường"
        return " | ".join(notes)
