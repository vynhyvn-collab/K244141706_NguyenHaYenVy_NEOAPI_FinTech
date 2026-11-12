"""
Module cấu hình dự án Smart Stock Screener.
Quản lý biến môi trường, bảo mật thông tin và tham số vận hành.
"""
import os
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # 1. VPBankS NEO API Configuration
    NEO_CONSUMER_KEY: str = Field(default="", description="VPBankS Consumer Key")
    NEO_CONSUMER_SECRET: str = Field(default="", description="VPBankS Consumer Secret")
    NEO_ACCOUNT_NO: str = Field(default="", description="Tài khoản giao dịch VPBankS")
    
    NEO_ENVIRONMENT: Literal["LIVE", "MOCK"] = Field(
        default="MOCK",
        description="Môi trường kết nối: LIVE (khi có API key) hoặc MOCK (mô phỏng dữ liệu chuẩn)"
    )
    NEO_API_BASE_URL: str = Field(
        default="https://neoinvest.vpbanks.com.vn/neo-openapi",
        description="Base URL REST API của NEO"
    )
    NEO_WS_URL: str = Field(
        default="wss://neoinvest.vpbanks.com.vn/neo-openapi/streaming",
        description="WebSocket URL của NEO"
    )
    NEO_RATE_LIMIT_RPS: float = Field(
        default=5.0,
        description="Giới hạn tối đa số request/giây (NEO quy định 5 req/s)"
    )

    # 2. SSI FastConnect API (Tùy chọn bổ trợ)
    SSI_CONSUMER_ID: str = Field(default="", description="SSI FastConnect Consumer ID")
    SSI_CONSUMER_SECRET: str = Field(default="", description="SSI Consumer Secret")
    SSI_PRIVATE_KEY_PATH: str = Field(default="", description="Đường dẫn file RSA Private Key")

    # 3. App Settings
    APP_ENV: str = Field(default="development", description="Môi trường ứng dụng")
    APP_PORT: int = Field(default=8501, description="Cổng chạy Streamlit")
    DATA_CACHE_DIR: str = Field(default="./data_sample", description="Thư mục cache dữ liệu")
    DEFAULT_UNIVERSE: str = Field(default="VN30", description="Rổ cổ phiếu mặc định")


# Singleton instance
settings = Settings()
