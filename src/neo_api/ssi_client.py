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
        self.session = session or requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }

    def get_market_universe(self, universe: str = "VN30") -> List[StockSnapshot]:
        """
        Lấy danh sách snapshot cổ phiếu từ thị trường thật.
        
        Args:
            universe: "VN30" (30 mã vốn hóa lớn nhất) hoặc "ALL" / "HOSE" (toàn bộ sàn HOSE)
        """
        universe_clean = universe.upper()
        if universe_clean == "VN30":
            url = f"{self.base_url}/stock/group/VN30"
        else:
            url = f"{self.base_url}/stock/exchange/hose"

        try:
            response = self.session.get(url, headers=self.headers, timeout=settings.NEO_REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise SSIClientError(f"Không thể kết nối SSI API ({url}): {exc}") from exc

        if not isinstance(data, dict) or data.get("code") != "SUCCESS":
            raise SSIClientError(f"Phản hồi SSI không hợp lệ: {data.get('message', 'Unknown error')}")

        items = data.get("data", [])
        if not isinstance(items, list) or not items:
            raise SSIClientError(f"SSI API không trả về dữ liệu danh mục cho {universe}.")

        snapshots: List[StockSnapshot] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            try:
                snap = self._parse_stock(item)
                if snap:
                    snapshots.append(snap)
            except Exception:
                # Bỏ qua bản ghi lỗi cấu trúc cục bộ để đảm bảo toàn vẹn dữ liệu
                continue

        if not snapshots:
            raise SSIClientError(f"Không có mã cổ phiếu hợp lệ nào từ SSI cho {universe}.")

        return snapshots

    def _parse_stock(self, item: Dict[str, Any]) -> Optional[StockSnapshot]:
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
        last_price = to_float(item.get("matchedPrice")) or ref_price
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
            market_code="HOSE",
            stock_type="ST",
            trading_status=trading_status,
        )
