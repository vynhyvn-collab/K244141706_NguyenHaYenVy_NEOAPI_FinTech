"""
Module kiểm thử kết nối và định dạng dữ liệu từ NEO API Client.
"""
import pytest
from src.neo_api.client import NeoApiClient
from src.neo_api.models import StockSnapshot


def test_neo_client_authentication():
    client = NeoApiClient()
    assert client.authenticate() is True
    assert client.jwt_token is not None


def test_get_stock_snapshot_structure():
    client = NeoApiClient()
    snapshot = client.get_stock_snapshot("FPT")
    
    assert isinstance(snapshot, StockSnapshot)
    assert snapshot.symbol == "FPT"
    assert snapshot.reference_price > 0
    assert snapshot.last_price > 0
    assert snapshot.ceiling_price > snapshot.reference_price
    assert snapshot.floor_price < snapshot.reference_price
    assert snapshot.order_book is not None
    assert len(snapshot.order_book.bids) == 3
    assert len(snapshot.order_book.asks) == 3
    assert snapshot.foreign_trade is not None


def test_get_market_universe_vn30():
    client = NeoApiClient()
    universe = client.get_market_universe("VN30")
    
    assert len(universe) == 30
    symbols = [s.symbol for s in universe]
    assert "FPT" in symbols
    assert "HPG" in symbols
    assert "TCB" in symbols
