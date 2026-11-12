"""
Kiểm thử kết nối dữ liệu thực tế và Pydantic Models.
"""
from src.neo_api.client import NeoApiClient
from src.neo_api.models import StockSnapshot


def test_neo_client_initialization():
    client = NeoApiClient()
    assert client.authenticate() is True


def test_get_live_stock_snapshot():
    """Kiểm thử tải dữ liệu thời gian thực từ thị trường."""
    client = NeoApiClient()
    snapshots = client.fetch_live_snapshots(["FPT", "HPG"])
    
    assert len(snapshots) >= 1
    fpt = next((s for s in snapshots if s.symbol == "FPT"), snapshots[0])
    assert isinstance(fpt, StockSnapshot)
    assert fpt.last_price > 0
    assert fpt.reference_price > 0
    assert fpt.order_book is not None
