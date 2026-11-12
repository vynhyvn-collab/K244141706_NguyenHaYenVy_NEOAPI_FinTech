"""
Module Xếp hạng đa nhân tố (Multi-Factor Scoring & Ranking Engine).
Thuật toán chuẩn hóa Min-Max / Percentile kết hợp trọng số tài chính:
1. Động lượng giá (Momentum - Trọng số w1 = 0.25)
2. Thanh khoản & Đột biến Vol (Liquidity/Vol - Trọng số w2 = 0.25)
3. Dòng tiền nước ngoài (Foreign Flow - Trọng số w3 = 0.25)
4. Độ lệch Cung - Cầu sổ lệnh (Order Book Imbalance - Trọng số w4 = 0.25)

Composite Score = w1 * S_mom + w2 * S_liq + w3 * S_for + w4 * S_obi (Thang điểm 0 - 100).
Phân tầng tín hiệu:
- Top Buy (>= 75): Đồng thuận tăng giá từ cả Cung-Cầu, Khối ngoại và Thanh khoản.
- Accumulation (60 - < 75): Lực gom âm thầm (OBI cao, Vol ổn định).
- Neutral (40 - < 60): Trạng thái cân bằng, tích lũy đi ngang.
- Caution (< 40): Áp lực bán mạnh, OBI âm hoặc khối ngoại xả ròng.
"""
from typing import List, Dict
import pandas as pd
import numpy as np

from src.neo_api.models import StockSnapshot, FactorScores
from src.finance.indicators import FinancialIndicatorCalculator


class MultiFactorRankingEngine:
    """Động cơ tính điểm và xếp hạng đa nhân tố."""

    # Tỷ trọng chuẩn mực cho từng trụ cột phân tích
    DEFAULT_WEIGHTS = {
        "momentum": 0.25,
        "liquidity": 0.25,
        "foreign": 0.25,
        "order_book": 0.25
    }

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS
        # Chuẩn hóa tổng trọng số = 1.0
        total_w = sum(self.weights.values())
        self.weights = {k: v / total_w for k, v in self.weights.items()}

    def rank_universe(self, snapshots: List[StockSnapshot]) -> List[FactorScores]:
        """
        Xếp hạng toàn bộ rổ cổ phiếu (ví dụ: VN30) theo điểm tổng hợp.
        """
        if not snapshots:
            return []

        # 1. Trích xuất raw metrics
        raw_list = [FinancialIndicatorCalculator.compute_all_metrics(s) for s in snapshots]
        df = pd.DataFrame(raw_list)

        # 2. Chuẩn hóa từng nhân tố về thang điểm 0 - 100
        # A. Điểm Động lượng (Momentum Score): Kết hợp % thay đổi giá và vị thế trong ngày
        # Biên độ chuẩn % thay đổi [-5%, +5%]
        norm_pct = np.clip((df["pct_change"] + 5.0) / 10.0, 0.0, 1.0)
        norm_pos = np.clip(df["range_position"], 0.0, 1.0)
        df["momentum_score"] = (norm_pct * 0.6 + norm_pos * 0.4) * 100.0

        # B. Điểm Thanh khoản (Liquidity Score): Đột biến Vol (RelVol) và Giá trị giao dịch
        # RelVol: [0.5, 2.5]
        norm_rel_vol = np.clip((df["relative_volume"] - 0.5) / 2.0, 0.0, 1.0)
        df["liquidity_score"] = norm_rel_vol * 100.0

        # C. Điểm Khối ngoại (Foreign Score): Net Impact [-0.1, +0.1] (tức mua ròng chiếm đến 10% thanh khoản)
        norm_foreign = np.clip((df["foreign_net_impact"] + 0.1) / 0.2, 0.0, 1.0)
        df["foreign_score"] = norm_foreign * 100.0

        # D. Điểm OBI (Order Book Imbalance Score): OBI [-0.8, +0.8]
        norm_obi = np.clip((df["order_book_imbalance"] + 0.8) / 1.6, 0.0, 1.0)
        df["order_book_imbalance_score"] = norm_obi * 100.0

        # 3. Tính Điểm tổng hợp (Composite Score)
        df["composite_score"] = (
            self.weights["momentum"] * df["momentum_score"] +
            self.weights["liquidity"] * df["liquidity_score"] +
            self.weights["foreign"] * df["foreign_score"] +
            self.weights["order_book"] * df["order_book_imbalance_score"]
        ).round(1)

        # 4. Phân hạng Tín hiệu (Tier) và Tóm tắt giải thích
        results: List[FactorScores] = []
        for idx, row in df.iterrows():
            comp_score = row["composite_score"]
            tier = self._classify_tier(comp_score)
            summary = self._generate_explanation(row)

            score_obj = FactorScores(
                symbol=row["symbol"],
                timestamp=row["timestamp"],
                momentum_score=round(row["momentum_score"], 1),
                liquidity_score=round(row["liquidity_score"], 1),
                foreign_score=round(row["foreign_score"], 1),
                order_book_imbalance_score=round(row["order_book_imbalance_score"], 1),
                composite_score=comp_score,
                ranking_tier=tier,
                signal_summary=summary
            )
            results.append(score_obj)

        # Xếp hạng giảm dần theo Composite Score
        results.sort(key=lambda x: x.composite_score, reverse=True)
        return results

    @staticmethod
    def _classify_tier(score: float) -> str:
        """Phân loại nhóm khuyến nghị dựa trên ngưỡng định lượng rõ ràng."""
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
        """Tạo thuyết minh tự động có cơ sở tài chính cho từng mã cổ phiếu."""
        notes = []
        # Nhận diện OBI
        if row["order_book_imbalance"] > 0.2:
            notes.append(f"Cầu mua áp đảo (OBI {row['order_book_imbalance']:+.1%})")
        elif row["order_book_imbalance"] < -0.2:
            notes.append(f"Áp lực bán đè (OBI {row['order_book_imbalance']:+.1%})")

        # Nhận diện Đột biến Vol
        if row["relative_volume"] >= 1.3:
            notes.append(f"Vol đột biến {row['relative_volume']}x TB20")

        # Nhận diện Khối ngoại
        if row["foreign_net_value"] > 5_000_000_000:
            notes.append(f"Khối ngoại gom ròng +{row['foreign_net_value']/1e9:.1f} tỷ")
        elif row["foreign_net_value"] < -5_000_000_000:
            notes.append(f"Khối ngoại bán ròng {row['foreign_net_value']/1e9:.1f} tỷ")

        if not notes:
            return "Biến động bình thường theo nhịp thị trường"
        return " | ".join(notes)
