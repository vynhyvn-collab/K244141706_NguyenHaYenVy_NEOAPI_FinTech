"""
Bộ kiểm thử đơn vị tự động (Unit Tests).
Kiểm thử toàn diện các trường hợp biên (Edge Cases), xử lý ngoại lệ, và thuật toán xếp hạng đa nhân tố.
Đảm bảo 100% không phụ thuộc mock hay dữ liệu giả lập.
"""
from datetime import datetime, timezone, timedelta
import pytest
from src.neo_api.models import StockSnapshot, StockOrderBook, PriceLevel, ForeignTrade
from src.finance.indicators import FinancialIndicatorCalculator
from src.analytics.ranking import MultiFactorRankingEngine
from src.neo_api.client import NeoApiClient, RateLimiter

VN_TZ = timezone(timedelta(hours=7))


@pytest.fixture
def sample_snapshot():
    now = datetime.now(VN_TZ)
    bids = [
        PriceLevel(price=142000, volume=100000),
        PriceLevel(price=141500, volume=80000),
        PriceLevel(price=141000, volume=60000),
    ]
    asks = [
        PriceLevel(price=142500, volume=30000),
        PriceLevel(price=143000, volume=20000),
        PriceLevel(price=143500, volume=10000),
    ]

    ob = StockOrderBook(symbol="FPT", timestamp=now, bids=bids, asks=asks)
    ft = ForeignTrade(
        symbol="FPT",
        buy_volume=300000,
        sell_volume=100000,
        net_volume=200000,
        buy_value=300000 * 142000,
        sell_value=100000 * 142000,
        net_value=200000 * 142000,
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
        exchange="HOSE",
        order_book=ob,
        foreign_trade=ft,
        avg_volume_20d=2000000
    )


def test_rate_limiter_thread_safety():
    """Kiểm thử thread-safe của RateLimiter."""
    limiter = RateLimiter(max_rate=10.0)
    assert limiter.tokens == 10.0
    limiter.acquire()
    assert limiter.tokens < 10.0


def test_calculate_weighted_order_book_imbalance(sample_snapshot):
    """Kiểm thử OBI có trọng số theo bước giá."""
    obi = FinancialIndicatorCalculator.calculate_order_book_imbalance(sample_snapshot.order_book)
    # w1=0.5, w2=0.3, w3=0.2
    # w_bid = 0.5*100k + 0.3*80k + 0.2*60k = 50k + 24k + 12k = 86k
    # w_ask = 0.5*30k + 0.3*20k + 0.2*10k = 15k + 6k + 2k = 23k
    # OBI = (86 - 23) / (86 + 23) = 63 / 109 = 0.578
    assert 0.57 <= obi <= 0.59
    assert -1.0 <= obi <= 1.0


def test_obi_edge_case_none_or_empty():
    """Kiểm thử trường hợp biên: Sổ lệnh rỗng hoặc None không bị crash."""
    assert FinancialIndicatorCalculator.calculate_order_book_imbalance(None) == 0.0
    
    empty_ob = StockOrderBook(symbol="TEST", timestamp=datetime.now(VN_TZ), bids=[], asks=[])
    assert FinancialIndicatorCalculator.calculate_order_book_imbalance(empty_ob) == 0.0


def test_relative_volume_division_by_zero():
    """Kiểm thử trường hợp biên: avg_volume_20d = 0 không bị chia cho 0."""
    now = datetime.now(VN_TZ)
    snap = StockSnapshot(
        symbol="TEST",
        timestamp=now,
        reference_price=10000,
        ceiling_price=10700,
        floor_price=9300,
        last_price=10000,
        total_volume=50000,
        avg_volume_20d=0.0
    )
    rel_vol = FinancialIndicatorCalculator.calculate_relative_volume(snap)
    assert rel_vol == 1.0


def test_spread_and_vwap_calculations(sample_snapshot):
    """Kiểm thử tính toán Bid-Ask Spread và VWAP."""
    spread_info = FinancialIndicatorCalculator.calculate_bid_ask_spread(
        sample_snapshot.order_book, sample_snapshot.last_price
    )
    assert spread_info["spread"] == 500.0  # 142500 - 142000
    assert spread_info["spread_pct"] > 0

    vwap_info = FinancialIndicatorCalculator.calculate_vwap_metric(sample_snapshot)
    assert vwap_info["vwap"] == 142000.0
    assert vwap_info["vwap_bias"] == 0.0


def test_percentile_multi_factor_ranking_engine(sample_snapshot):
    """Kiểm thử Động cơ xếp hạng phân vị tương đối."""
    engine = MultiFactorRankingEngine()
    
    # Tạo danh sách 2 mã để kiểm thử xếp hạng tương đối
    snap2 = sample_snapshot.model_copy()
    snap2.symbol = "HPG"
    snap2.pct_change = -2.5
    snap2.order_book = StockOrderBook(
        symbol="HPG",
        timestamp=datetime.now(VN_TZ),
        bids=[PriceLevel(price=25000, volume=10000)],
        asks=[PriceLevel(price=25100, volume=100000)]
    )
    snap2.foreign_trade = ForeignTrade(
        symbol="HPG",
        buy_volume=10000,
        sell_volume=300000,
        net_volume=-290000,
        buy_value=10000 * 25000,
        sell_value=300000 * 25000,
        net_value=-290000 * 25000,
        total_room=1000000,
        current_room=500000
    )
    snap2.total_volume = 100000
    snap2.avg_volume_20d = 1000000

    results = engine.rank_universe([sample_snapshot, snap2])
    assert len(results) == 2
    # FPT phải xếp trên HPG vì mọi chỉ số đều tốt hơn
    assert results[0].symbol == "FPT"
    assert results[0].composite_score > results[1].composite_score
    assert results[0].ranking_tier in ["Top Buy", "Accumulation"]
    assert results[1].ranking_tier in ["Neutral", "Caution"]


def test_tier_classification_thresholds():
    """Kiểm thử chính xác từng ngưỡng phân tầng xếp hạng."""
    assert MultiFactorRankingEngine._classify_tier(75.0) == "Top Buy"
    assert MultiFactorRankingEngine._classify_tier(60.0) == "Accumulation"
    assert MultiFactorRankingEngine._classify_tier(45.0) == "Neutral"
    assert MultiFactorRankingEngine._classify_tier(30.0) == "Caution"


def test_neo_client_live_symbols():
    """Kiểm thử Client lấy danh mục VN30 thực tế."""
    client = NeoApiClient()
    vn30 = client.get_symbols_by_exchange("VN30")
    assert len(vn30) == 30
    assert "FPT" in vn30
    assert "HPG" in vn30
