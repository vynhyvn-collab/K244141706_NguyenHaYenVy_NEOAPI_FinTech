"""
Pydantic Data Models cho dữ liệu thị trường và vi cấu trúc từ NEO API.
Chuẩn hóa dữ liệu theo đúng định dạng thời gian Việt Nam (UTC+7).
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class PriceLevel(BaseModel):
    """Một bước giá trong sổ lệnh Top 3."""
    price: Optional[float] = Field(None, description="Mức giá số (VNĐ), None nếu API trả ATO/ATC")
    volume: int = Field(..., description="Khối lượng đặt tương ứng")
    raw_price: Optional[str] = Field(None, description="Giá gốc API nếu không phải giá số (ví dụ ATO/ATC)")


class StockOrderBook(BaseModel):
    """Sổ lệnh độ sâu 3 mức giá Mua/Bán từ NEO API."""
    symbol: str
    timestamp: datetime
    # 3 mức giá Mua tốt nhất (Bid 1, 2, 3)
    bids: List[PriceLevel] = Field(default_factory=list, description="Top 3 giá mua (giảm dần)")
    # 3 mức giá Bán tốt nhất (Ask 1, 2, 3)
    asks: List[PriceLevel] = Field(default_factory=list, description="Top 3 giá bán (tăng dần)")


class ForeignTrade(BaseModel):
    """Giao dịch khối ngoại theo mã."""
    symbol: str
    buy_volume: int = 0
    sell_volume: int = 0
    net_volume: int = 0
    buy_value: Optional[float] = None
    sell_value: Optional[float] = None
    net_value: Optional[float] = None
    total_room: int = 0
    current_room: int = 0


class StockSnapshot(BaseModel):
    """Ảnh chụp thị trường của một cổ phiếu tại một thời điểm."""
    symbol: str
    timestamp: datetime
    reference_price: float = Field(..., description="Giá tham chiếu")
    ceiling_price: float = Field(..., description="Giá trần")
    floor_price: float = Field(..., description="Giá sàn")
    open_price: float = 0.0
    high_price: float = 0.0
    low_price: float = 0.0
    last_price: float = Field(..., description="Giá khớp gần nhất")
    last_volume: int = 0
    total_volume: int = Field(0, description="Tổng khối lượng khớp trong phiên")
    total_value: float = Field(0.0, description="Tổng giá trị khớp (VNĐ)")
    change: float = Field(0.0, description="Biến động giá tuyệt đối")
    pct_change: Optional[float] = Field(None, description="Tỷ lệ biến động giá (%)")
    
    # Dữ liệu vi cấu trúc
    order_book: Optional[StockOrderBook] = None
    foreign_trade: Optional[ForeignTrade] = None

    # Metadata được trả về từ stockDetail / stockDetailByIndex.
    market_code: Optional[str] = None
    stock_type: Optional[str] = None
    trading_status: Optional[str] = None
    
class FactorScores(BaseModel):
    """Điểm số các nhân tố tài chính vi cấu trúc."""
    symbol: str
    timestamp: datetime
    momentum_score: Optional[float] = Field(None, description="Điểm Động lượng giá (0 - 100)")
    liquidity_score: Optional[float] = Field(None, description="Điểm percentile từ totalTradingValue phiên")
    foreign_score: Optional[float] = Field(None, description="Điểm Dòng tiền nước ngoài (0 - 100)")
    order_book_imbalance_score: Optional[float] = Field(None, description="Điểm Độ lệch cung - cầu OBI (0 - 100)")
    composite_score: Optional[float] = Field(None, description="Điểm xếp hạng tổng hợp (0 - 100), null nếu thiếu dữ liệu")
    ranking_tier: str = Field(..., description="Nhóm điểm tương đối; có thể là Thiếu dữ liệu")
    signal_summary: str = Field(..., description="Tóm tắt tín hiệu giải thích cho nhà đầu tư")
