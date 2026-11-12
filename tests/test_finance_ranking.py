"""
Kiểm thử đơn vị cho Module Tài chính (src/finance/) và Xếp hạng (src/analytics/).
Đảm bảo tính chính xác của các công thức tài chính và cơ chế xếp hạng.
"""
from datetime import datetime, timezone, timedelta
import pytest
from src.neo_api.models import StockSnapshot, StockOrderBook, PriceLevel, ForeignTrade
from src.finance.indicators import FinancialIndicatorCalculator
from src.analytics.ranking import MultiFactorRankingEngine

VN_TZ = timezone(timedelta(hours=7))


@pytest.fixture
def sample_snapshot():
    now = datetime.now(VN_TZ)
    # Giả lập cổ phiếu FPT với lực Cầu mua mạnh (OBI > 0)
    bids = [
        PriceLevel(price=142000, volume=100000),
        PriceLevel(price=141500, volume=80000),
        PriceLevel(price=141000, volume=60000),
    ] # Tổng Bid = 240,000
    asks = [
        PriceLevel(price=142500, volume=30000),
        PriceLevel(price=143000, volume=20000),
        PriceLevel(price=143500, volume=10000),
    ] # Tổng Ask = 60,000

    ob = StockOrderBook(symbol="FPT", timestamp=now, bids=bids, asks=asks)
    ft = ForeignTrade(
        symbol="FPT",
        buy_volume=300000,
        sell_volume=100000,
        net_volume=200000,
        buy_value=300000 * 142000,
        sell_value=100000 * 142000,
        net_value=200000 * 142000, # Mua ròng
        total_room=1000000,
        current_room=500000
    )

    return StockSnapshot(
        symbol="FPT",
        timestamp=now,
        reference_price=140000,
        ceiling_price=149800,
        floor_price=130200,
        open_price=140500,
        high_price=142500,
        low_price=140000,
        last_price=142000,
        last_volume=5000,
        total_volume=3000000,
        total_value=3000000 * 142000,
        change=2000,
        pct_change=1.43,
        order_book=ob,
        foreign_trade=ft,
        avg_volume_20d=2000000 # RelVol = 1.5x
    )


def test_calculate_order_book_imbalance(sample_snapshot):
    obi = FinancialIndicatorCalculator.calculate_order_book_imbalance(sample_snapshot.order_book)
    # Total Bid = 240,000, Total Ask = 60,000 -> OBI = (240k - 60k) / (240k + 60k) = 180 / 300 = 0.6
    assert obi == 0.6
    assert -1.0 <= obi <= 1.0


def test_calculate_relative_volume(sample_snapshot):
    rel_vol = FinancialIndicatorCalculator.calculate_relative_volume(sample_snapshot)
    # 3,000,000 / 2,000,000 = 1.5
    assert rel_vol == 1.5


def test_multi_factor_ranking_engine(sample_snapshot):
    engine = MultiFactorRankingEngine()
    results = engine.rank_universe([sample_snapshot])
    
    assert len(results) == 1
    res = results[0]
    assert res.symbol == "FPT"
    assert 0.0 <= res.composite_score <= 100.0
    assert 0.0 <= res.order_book_imbalance_score <= 100.0
    assert 0.0 <= res.liquidity_score <= 100.0
    assert 0.0 <= res.foreign_score <= 100.0
    assert 0.0 <= res.momentum_score <= 100.0
    assert res.ranking_tier in ["Top Buy", "Accumulation", "Neutral", "Caution"]
    assert "Cầu mua áp đảo" in res.signal_summary or "Vol đột biến" in res.signal_summary
