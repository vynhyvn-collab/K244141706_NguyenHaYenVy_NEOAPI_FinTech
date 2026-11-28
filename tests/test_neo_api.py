"""Kiểm thử client NeoAPI bằng response mẫu theo đúng cấu trúc tài liệu, không gọi mạng."""
from src.neo_api.client import NeoApiClient, NeoApiError
from src.neo_api.config import settings


class ResponseStub:
    def __init__(self, body):
        self.body = body

    def raise_for_status(self):
        return None

    def json(self):
        return self.body


class SessionStub:
    def __init__(self, pages=None):
        self.pages = pages or {}
        self.post_calls = []
        self.get_calls = []

    def post(self, url, json, timeout):
        self.post_calls.append((url, json, timeout))
        return ResponseStub({"status": 1, "data": {"access_token": "test-jwt", "expires_in": 10800}})

    def get(self, url, headers, params, timeout):
        self.get_calls.append((url, headers, params, timeout))
        return ResponseStub(self.pages[url.rsplit("/", 1)[-1] + str(params["pageNo"])])


def stock(symbol="VPB"):
    return {
        "symbol": symbol, "marketCode": "HOSE", "stockType": "ST", "tradingStatus": "NORMAL",
        "refPrice": 31600, "closePrice": 31250, "priceChange": -350,
        "percentPriceChange": -1.11, "openPrice": 31500, "highPrice": 32200, "lowPrice": 31100,
        "closeVol": 5000, "totalTradingVolume": 33498000, "totalTradingValue": 1052566395000,
        "bidPrice1": "31250.0", "bidVol1": 98500, "bidPrice2": 31200, "bidVol2": 608000,
        "bidPrice3": 31150, "bidVol3": 560800, "askPrice1": "31300.0", "askVol1": 590900,
        "askPrice2": 31350, "askVol2": 103600, "askPrice3": 31400, "askVol3": 201200,
        "foreignBuyVolume": 2924700, "foreignSellVolume": 2334102,
        "foreignBuyValue": 91396875000, "foreignSellValue": 72940687500,
        "foreignRemain": 435283768, "foreignRoom": 2380177080,
    }


def page(rows, page_no, total_pages):
    return {"status": 1, "data": {"content": rows, "pageable": {"pageNumber": page_no - 1}, "totalPages": total_pages}}


def configure_credentials(monkeypatch):
    monkeypatch.setattr(settings, "NEO_USERNAME", "test-user")
    monkeypatch.setattr(settings, "NEO_PASSWORD", "test-password")


def test_authentication_uses_documented_credentials(monkeypatch):
    configure_credentials(monkeypatch)
    session = SessionStub()
    client = NeoApiClient(session=session)

    assert client.authenticate() is True
    assert client.jwt_token == "test-jwt"
    url, payload, _ = session.post_calls[0]
    assert url == settings.NEO_AUTH_URL
    assert payload == {"username": "test-user", "password": "test-password"}


def test_stock_detail_maps_documented_fields_and_paginates(monkeypatch):
    configure_credentials(monkeypatch)
    base_url = settings.NEO_API_BASE_URL.rstrip("/")
    session = SessionStub({
        "stockDetail1": page([stock("VPB")], 1, 2),
        "stockDetail2": page([stock("HPG")], 2, 2),
    })
    client = NeoApiClient(session=session)
    client.jwt_token, client.token_expiry = "test-jwt", 10**12

    result = client.get_market_universe("ALL")
    assert [item.symbol for item in result] == ["VPB", "HPG"]
    assert result[0].market_code == "HOSE"
    assert result[0].last_price == 31250
    assert result[0].total_volume == 33498000
    assert result[0].foreign_trade.net_value == 18456187500
    assert result[0].order_book.bids[0].price == 31250
    assert len(session.get_calls) == 2
    _, headers, params, _ = session.get_calls[0]
    assert headers["Authorization"] == "Bearer test-jwt"
    assert headers["x-device"] == settings.NEO_DEVICE
    assert headers["x-devicetype"] == settings.NEO_DEVICE_TYPE
    assert params == {"marketCode": "ALL", "pageNo": 1, "pageSize": 1000}
    assert session.get_calls[0][0] == f"{base_url}/stock/stockDetail"


def test_universe_vn30_uses_documented_index_endpoint(monkeypatch):
    configure_credentials(monkeypatch)
    session = SessionStub({"stockDetailByIndex1": page([stock()], 1, 1)})
    client = NeoApiClient(session=session)
    client.jwt_token, client.token_expiry = "test-jwt", 10**12

    assert client.get_market_universe("VN30")[0].symbol == "VPB"
    assert session.get_calls[0][0].endswith("/stock/stockDetailByIndex")
    assert session.get_calls[0][2]["indexCode"] == "VN30"


def test_authentication_fails_closed_without_credentials(monkeypatch):
    monkeypatch.setattr(settings, "NEO_USERNAME", "")
    monkeypatch.setattr(settings, "NEO_PASSWORD", "")
    try:
        NeoApiClient(session=SessionStub()).authenticate()
        assert False, "Expected missing-credentials failure"
    except NeoApiError as exc:
        assert "Thiếu NEO_USERNAME" in str(exc)


def test_ssi_client_parsing():
    from src.neo_api.ssi_client import SSIClient

    class SSISessionStub:
        def get(self, url, headers, timeout):
            sample_data = {
                "code": "SUCCESS",
                "data": [{
                    "stockSymbol": "ACB",
                    "refPrice": 19600,
                    "ceiling": 20950,
                    "floor": 18250,
                    "openPrice": 19600,
                    "highest": 19800,
                    "lowest": 19550,
                    "matchedPrice": 19750,
                    "matchedVolume": 14500,
                    "priceChange": 150,
                    "priceChangePercent": 0.77,
                    "stockVol": 4969000,
                    "nmTotalTradedValue": 97467280000,
                    "best1Bid": 19700,
                    "best1BidVol": 36100,
                    "best1Offer": 19750,
                    "best1OfferVol": 552300,
                    "best2Bid": 19650,
                    "best2BidVol": 150200,
                    "best2Offer": 19800,
                    "best2OfferVol": 61800,
                    "best3Bid": 19600,
                    "best3BidVol": 298300,
                    "best3Offer": 19850,
                    "best3OfferVol": 132000,
                    "buyForeignQtty": 677500,
                    "buyForeignValue": 13350690000,
                    "sellForeignQtty": 744059,
                    "sellForeignValue": 14589059350,
                    "remainForeignQtty": 468985124,
                    "adminStatus": "NRM"
                }]
            }
            return ResponseStub(sample_data)

    client = SSIClient(session=SSISessionStub())
    snapshots = client.get_market_universe("VN30")
    assert len(snapshots) == 1
    s = snapshots[0]
    assert s.symbol == "ACB"
    assert s.last_price == 19750
    assert s.pct_change == 0.77
    assert len(s.order_book.bids) == 3
    assert s.order_book.bids[0].price == 19700
    assert s.order_book.bids[0].volume == 36100
    assert s.foreign_trade.buy_volume == 677500
    assert s.foreign_trade.sell_volume == 744059
    assert s.foreign_trade.net_value == (13350690000 - 14589059350)
    assert s.trading_status == "NORMAL"


def test_neo_client_connection_status_and_ip_whitelisting(monkeypatch):
    configure_credentials(monkeypatch)
    monkeypatch.setattr(settings, "NEO_WHITELIST_IP", "192.0.2.1")
    client = NeoApiClient(session=SessionStub())
    client.current_ip = "192.0.2.1"
    status = client.get_connection_status()

    assert status["whitelisted_ip"] == "192.0.2.1"
    assert status["current_ip"] == "192.0.2.1"
    assert status["is_ip_matched"] is True
    assert "100%" in status["data_quality"]
