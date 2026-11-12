"""
Pydantic Data Models cho dữ liệu thị trường và vi cấu trúc.
Chuẩn hóa dữ liệu theo đúng định dạng thời gian Việt Nam (UTC+7).
Không chứa mã giả lập hay phụ thuộc mock.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class PriceLevel(BaseModel):
    """Một bước giá trong sổ lệnh Top 3."""
    price: float = Field(..., description="Mức giá (VNĐ)")
    volume: int = Field(..., description="Khối lượng đặt tương ứng (cổ phiếu)")


class StockOrderBook(BaseModel):
    """Sổ lệnh độ sâu 3 mức giá Mua/Bán vi cấu trúc."""
    symbol: str
    timestamp: datetime
    # 3 mức giá Mua tốt nhất (Bid 1, 2, 3)
    bids: List[PriceLevel] = Field(default_factory=list, description="Top 3 giá mua (giảm dần)")
    # 3 mức giá Bán tốt nhất (Ask 1, 2, 3)
    asks: List[PriceLevel] = Field(default_factory=list, description="Top 3 giá bán (tăng dần)")


class ForeignTrade(BaseModel):
    """Dữ liệu giao dịch của khối ngoại."""
    symbol: str
    buy_volume: int = 0
    sell_volume: int = 0
    net_volume: int = 0
    buy_value: float = 0.0
    sell_value: float = 0.0
    net_value: float = 0.0
    total_room: int = 0
    current_room: int = 0


class StockSnapshot(BaseModel):
    """Ảnh chụp thị trường thực tế của một cổ phiếu."""
    symbol: str
    timestamp: datetime
    reference_price: float = Field(..., description="Giá tham chiếu (VNĐ)")
    ceiling_price: float = Field(..., description="Giá trần (VNĐ)")
    floor_price: float = Field(..., description="Giá sàn (VNĐ)")
    open_price: float = 0.0
    high_price: float = 0.0
    low_price: float = 0.0
    last_price: float = Field(..., description="Giá khớp gần nhất (VNĐ)")
    last_volume: int = 0
    total_volume: int = Field(0, description="Tổng khối lượng khớp trong phiên (cổ phiếu)")
    total_value: float = Field(0.0, description="Tổng giá trị khớp (VNĐ)")
    change: float = Field(0.0, description="Biến động giá tuyệt đối (VNĐ)")
    pct_change: float = Field(0.0, description="Tỷ lệ biến động giá (%)")
    exchange: str = Field("HOSE", description="Sàn giao dịch: HOSE, HNX, UPCOM")
    
    # Dữ liệu vi cấu trúc sổ lệnh
    order_book: Optional[StockOrderBook] = None
    foreign_trade: Optional[ForeignTrade] = None
    
    # Chỉ số lịch sử để so sánh
    avg_volume_20d: float = Field(0.0, description="Khối lượng trung bình 20 phiên gần nhất")


class FactorScores(BaseModel):
    """Điểm số các nhân tố tài chính vi cấu trúc."""
    symbol: str
    timestamp: datetime
    momentum_score: float = Field(..., description="Điểm Động lượng giá (0 - 100)")
    liquidity_score: float = Field(..., description="Điểm Thanh khoản & Khối lượng đột biến (0 - 100)")
    foreign_score: float = Field(..., description="Điểm Dòng tiền nước ngoài (0 - 100)")
    order_book_imbalance_score: float = Field(..., description="Điểm Độ lệch cung - cầu sổ lệnh OBI (0 - 100)")
    composite_score: float = Field(..., description="Điểm xếp hạng tổng hợp (0 - 100)")
    ranking_tier: str = Field(..., description="Phân loại: Top Buy, Accumulation, Neutral, Caution")
    signal_summary: str = Field(..., description="Tóm tắt tín hiệu giải thích định lượng")
