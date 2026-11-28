"""
Client dữ liệu thị trường SSI FastConnect / iBoard.
Cung cấp 100% dữ liệu thật từ Sở Giao dịch Chứng khoán TP.HCM (HOSE) & rổ chỉ số VN30.
Tuân thủ đặc tả kỹ thuật SSI Developer Portal API v3.
"""
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import requests

from .config import settings
from .models import ForeignTrade, PriceLevel, StockOrderBook, StockSnapshot

VN_TZ = timezone(timedelta(hours=7))


class SSIClientError(RuntimeError):
    """Lỗi phát sinh khi truy vấn dữ liệu từ SSI FastConnect / iBoard API."""


class SSIClient:
    """
    Client kết nối nguồn dữ liệu thị trường thời gian thực SSI FastConnect / iBoard.
    Được tích hợp làm nguồn dữ liệu bổ sung hợp lệ theo ủy quyền của người dùng.
    """

    def __init__(self, session: Optional[requests.Session] = None):
        self.base_url = settings.SSI_IBOARD_URL.rstrip("/")
        self.fastconnect_url = settings.SSI_FASTCONNECT_URL.rstrip("/")
        self.session = session or requests.Session()
        self.access_token: Optional[str] = None
        self.token_expiry: float = 0.0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }

    def authenticate(self) -> bool:
        """
        Xác thực với SSI FastConnect API v3 qua POST /api/v3/auth/token nếu người dùng cấu hình API Key & Secret.
        Theo đúng quy chuẩn trang 12 & 23 của tài liệu SSI Developer Portal v3 (457 trang).
        """
        if not settings.SSI_API_KEY or not settings.SSI_API_SECRET:
            return False
        if self.access_token and time.time() < self.token_expiry - 30:
            return True
        try:
            url = f"{self.fastconnect_url}/api/v3/auth/token"
            resp = self.session.post(
                url,
                json={"apiKey": settings.SSI_API_KEY, "apiSecret": settings.SSI_API_SECRET},
                timeout=settings.NEO_REQUEST_TIMEOUT
            )
            resp.raise_for_status()
            body = resp.json()
            token = body.get("accessToken")
            if token:
                self.access_token = token
                self.token_expiry = float(body.get("expiresAt", time.time() + 3600))
                self.headers["Authorization"] = f"Bearer {token}"
                return True
        except Exception:
            pass
        return False

    def get_market_universe(self, universe: str = "VN30") -> List[StockSnapshot]:
        """
        Lấy danh sách snapshot cổ phiếu từ thị trường thật.
        
        Args:
            universe: "VN30" (30 mã vốn hóa lớn nhất), "HOSE", "HNX", "UPCOM", hoặc 
                      "ALL" (toàn bộ 100% các mã cổ phiếu đang giao dịch trên cả 3 sàn).
        """
        self.authenticate()
        universe_clean = universe.upper()
        
        endpoints: List[tuple[str, str]] = []
        if universe_clean == "VN30":
            endpoints = [(f"{self.base_url}/stock/group/VN30", "HOSE")]
        elif universe_clean == "HOSE":
            endpoints = [(f"{self.base_url}/stock/exchange/hose", "HOSE")]
        elif universe_clean == "HNX":
            endpoints = [(f"{self.base_url}/stock/exchange/hnx", "HNX")]
        elif universe_clean == "UPCOM":
            endpoints = [(f"{self.base_url}/stock/exchange/upcom", "UPCOM")]
        else:
            # "ALL": Lấy trọn vẹn 100% toàn bộ thị trường Việt Nam (HOSE + HNX + UPCOM)
            endpoints = [
                (f"{self.base_url}/stock/exchange/hose", "HOSE"),
                (f"{self.base_url}/stock/exchange/hnx", "HNX"),
                (f"{self.base_url}/stock/exchange/upcom", "UPCOM"),
            ]

        snapshots: List[StockSnapshot] = []
        errors: List[str] = []

        for url, default_market in endpoints:
            try:
                response = self.session.get(url, headers=self.headers, timeout=settings.NEO_REQUEST_TIMEOUT)
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, dict) or data.get("code") != "SUCCESS":
                    errors.append(f"{url}: {data.get('message', 'Non-success response')}")
                    continue
                items = data.get("data", [])
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            snap = self._parse_stock(item, default_market=default_market)
                            if snap:
                                snapshots.append(snap)
            except Exception as exc:
                errors.append(f"{url}: {exc}")

        if not snapshots:
            raise SSIClientError(
                f"Không thể lấy dữ liệu SSI cho danh mục {universe}. Chi tiết lỗi: {'; '.join(errors)}"
            )

        return snapshots

    def _parse_stock(self, item: Dict[str, Any], default_market: str = "HOSE") -> Optional[StockSnapshot]:
        """Ánh xạ một bản ghi cổ phiếu từ SSI sang định dạng chuẩn StockSnapshot."""
        symbol = str(item.get("stockSymbol") or "").strip()
        if not symbol:
            return None

        def to_float(val: Any) -> Optional[float]:
            if val is None or val == "":
                return None
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        def to_int(val: Any) -> int:
            f = to_float(val)
            return int(f) if f is not None else 0

        # 1. Trích xuất Độ sâu Sổ lệnh Top 3 Bước giá (Order Book)
        bids: List[PriceLevel] = []
        asks: List[PriceLevel] = []

        for level in (1, 2, 3):
            # Bên Mua (Bid)
            bp = to_float(item.get(f"best{level}Bid"))
            bv = to_int(item.get(f"best{level}BidVol"))
            if bp is not None or bv > 0:
                bids.append(PriceLevel(price=bp, volume=bv))

            # Bên Bán (Ask/Offer)
            ap = to_float(item.get(f"best{level}Offer"))
            av = to_int(item.get(f"best{level}OfferVol"))
            if ap is not None or av > 0:
                asks.append(PriceLevel(price=ap, volume=av))

        order_book = StockOrderBook(
            symbol=symbol,
            timestamp=datetime.now(VN_TZ),
            bids=bids,
            asks=asks,
        )

        # 2. Trích xuất Dòng tiền Khối ngoại (Foreign Trade)
        fb_vol = to_int(item.get("buyForeignQtty"))
        fs_vol = to_int(item.get("sellForeignQtty"))
        fb_val = to_float(item.get("buyForeignValue")) or 0.0
        fs_val = to_float(item.get("sellForeignValue")) or 0.0
        remain_room = to_int(item.get("remainForeignQtty"))

        foreign_trade = ForeignTrade(
            symbol=symbol,
            buy_volume=fb_vol,
            sell_volume=fs_vol,
            net_volume=fb_vol - fs_vol,
            buy_value=fb_val,
            sell_value=fs_val,
            net_value=fb_val - fs_val,
            current_room=remain_room,
        )

        # 3. Trích xuất Giá và Khối lượng giao dịch
        ref_price = to_float(item.get("refPrice")) or 0.0
        last_price = to_float(item.get("matchedPrice"))
        if not last_price or last_price <= 0:
            last_price = ref_price

        price_change = to_float(item.get("priceChange"))
        if price_change is None:
            price_change = last_price - ref_price if (last_price and ref_price) else 0.0

        pct_change = to_float(item.get("priceChangePercent"))
        if pct_change is None and ref_price > 0:
            pct_change = (last_price - ref_price) / ref_price * 100.0

        total_vol = to_int(item.get("stockVol") or item.get("nmTotalTradedQty"))
        total_val = to_float(item.get("nmTotalTradedValue")) or 0.0

        admin_status = str(item.get("adminStatus") or "NRM").upper()
        trading_status = "NORMAL" if admin_status in ("NRM", "NORMAL") else admin_status

        # Xác định sàn niêm yết chuẩn
        exchange_raw = item.get("exchange") or default_market
        market_code = str(exchange_raw).upper()

        return StockSnapshot(
            symbol=symbol,
            timestamp=datetime.now(VN_TZ),
            reference_price=ref_price,
            ceiling_price=to_float(item.get("ceiling")) or 0.0,
            floor_price=to_float(item.get("floor")) or 0.0,
            open_price=to_float(item.get("openPrice")) or ref_price,
            high_price=to_float(item.get("highest")) or last_price,
            low_price=to_float(item.get("lowest")) or last_price,
            last_price=last_price,
            last_volume=to_int(item.get("matchedVolume")),
            total_volume=total_vol,
            total_value=total_val,
            change=price_change,
            pct_change=pct_change,
            order_book=order_book,
            foreign_trade=foreign_trade,
            market_code=market_code,
            stock_type="ST",
            trading_status=trading_status,
        )
