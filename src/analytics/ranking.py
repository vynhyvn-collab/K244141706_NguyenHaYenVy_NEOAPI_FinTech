"""Xếp hạng đa nhân tố từ các trường thực có trong tài liệu VPBankS NeoAPI."""
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from src.finance.indicators import FinancialIndicatorCalculator
from src.neo_api.models import FactorScores, StockSnapshot


class MultiFactorRankingEngine:
    """Xếp hạng tương đối trong universe; thiếu dữ liệu thì bỏ qua nhân tố."""

    DEFAULT_WEIGHTS = {"momentum": 0.30, "liquidity": 0.25, "foreign": 0.25, "order_book": 0.20}

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = dict(weights or self.DEFAULT_WEIGHTS)
        if set(self.weights) != set(self.DEFAULT_WEIGHTS):
            raise ValueError(f"weights phải có các khóa: {', '.join(self.DEFAULT_WEIGHTS)}")
        if any(value < 0 for value in self.weights.values()) or sum(self.weights.values()) <= 0:
            raise ValueError("Trọng số phải không âm và tổng trọng số lớn hơn 0.")
        total = sum(self.weights.values())
        self.weights = {name: value / total for name, value in self.weights.items()}

    @staticmethod
    def _percentile(values: pd.Series) -> pd.Series:
        """Điểm percentile 0–100; tập đơn phần tử/đồng hạng cho điểm trung tính 50."""
        numeric = pd.to_numeric(values, errors="coerce")
        result = pd.Series(np.nan, index=values.index, dtype=float)
        valid = numeric.dropna()
        if valid.empty:
            return result
        if len(valid) == 1 or valid.nunique() == 1:
            result.loc[valid.index] = 50.0
        else:
            result.loc[valid.index] = valid.rank(method="average", pct=True) * 100.0
        return result

    def rank_universe(self, snapshots: List[StockSnapshot]) -> List[FactorScores]:
        if not snapshots:
            return []
        rows = [FinancialIndicatorCalculator.compute_all_metrics(item) for item in snapshots]
        df = pd.DataFrame(rows)

        # NeoAPI stockDetail supplies only current-session price/volume, not 20-session history.
        pct_rank = self._percentile(df["pct_change"])
        range_rank = self._percentile(df["range_position"])
        df["momentum_score"] = pd.concat([pct_rank, range_rank], axis=1).mean(axis=1, skipna=True)
        df.loc[df[["pct_change", "range_position"]].isna().all(axis=1), "momentum_score"] = np.nan

        # Use documented totalTradingValue as session liquidity; no synthetic RelVol / MA20.
        df["liquidity_score"] = self._percentile(df["total_value"].where(df["total_value"] > 0))
        df["foreign_score"] = self._percentile(df["foreign_net_impact"])
        df["order_book_imbalance_score"] = self._percentile(df["order_book_imbalance"])

        score_columns = {
            "momentum_score": self.weights["momentum"],
            "liquidity_score": self.weights["liquidity"],
            "foreign_score": self.weights["foreign"],
            "order_book_imbalance_score": self.weights["order_book"],
        }
        weighted = df[list(score_columns)].mul(pd.Series(score_columns), axis="columns")
        active_weights = df[list(score_columns)].notna().mul(pd.Series(score_columns), axis="columns")
        df["composite_score"] = (
            weighted.sum(axis=1, min_count=1) / active_weights.sum(axis=1).replace(0, np.nan)
        ).round(1)

        output = []
        for _, row in df.iterrows():
            score = row["composite_score"]
            score_missing = pd.isna(score)
            if score_missing:
                score = None
            output.append(FactorScores(
                symbol=row["symbol"], timestamp=row["timestamp"],
                momentum_score=self._optional_score(row["momentum_score"]),
                liquidity_score=self._optional_score(row["liquidity_score"]),
                foreign_score=self._optional_score(row["foreign_score"]),
                order_book_imbalance_score=self._optional_score(row["order_book_imbalance_score"]),
                composite_score=None if score_missing else float(score),
                ranking_tier="Thiếu dữ liệu" if score_missing else self._classify_tier(float(score)),
                signal_summary=self._generate_explanation(row),
            ))
        return sorted(output, key=lambda item: item.composite_score if item.composite_score is not None else -1, reverse=True)

    @staticmethod
    def _optional_score(value) -> Optional[float]:
        return round(float(value), 1) if pd.notna(value) else None

    @staticmethod
    def _classify_tier(score: float) -> str:
        if score >= 75:
            return "Mạnh"
        if score >= 60:
            return "Tích cực"
        if score >= 40:
            return "Trung tính"
        return "Yếu"

    @staticmethod
    def _generate_explanation(row: pd.Series) -> str:
        notes = []
        if pd.notna(row.get("pct_change")):
            notes.append(f"Biến động phiên {row['pct_change']:+.2f}%")
        obi = row.get("order_book_imbalance")
        if pd.notna(obi):
            notes.append(f"OBI Top 3 {obi:+.1%}")
        foreign_net = row.get("foreign_net_value")
        if pd.notna(foreign_net):
            notes.append(f"Khối ngoại ròng {foreign_net / 1e9:+.2f} tỷ VNĐ")
        return " | ".join(notes) if notes else "Một số nhân tố không có dữ liệu từ API"
