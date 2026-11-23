"""
Module cấu hình dự án Smart Stock Screener.
Quản lý biến môi trường, bảo mật thông tin và tham số vận hành.
"""
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
    NEO_USERNAME: str = Field(default="", description="Tên đăng nhập VPBankS (số lưu ký)")
    NEO_PASSWORD: str = Field(default="", description="Mật khẩu đăng nhập VPBankS")
    NEO_ACCOUNT_NO: str = Field(default="", description="Tài khoản giao dịch VPBankS")
    NEO_WHITELIST_IP: str = Field(
        default="",
        description="Địa chỉ IP tĩnh được đăng ký whitelist, chỉ cấu hình trong môi trường bí mật"
    )

    NEO_ENVIRONMENT: Literal["LIVE", "UAT"] = Field(
        default="LIVE",
        description="Môi trường NeoAPI: LIVE (production) hoặc UAT (kiểm thử)",
    )
    NEO_API_BASE_URL: str = Field(
        default="https://neoapi.vpbanks.com.vn/neo-api",
        description="Base URL REST NeoAPI; UAT: https://neopro-uat.vpbanks.com.vn/neo-api",
    )
    NEO_AUTH_URL: str = Field(
        default="https://external.vpbanks.com.vn/auth/token",
        description="Endpoint đăng nhập lấy JWT theo tài liệu NeoAPI",
    )
    NEO_DEVICE: str = Field(default="neoapi-fintech-dashboard", description="Header x-device")
    NEO_DEVICE_TYPE: str = Field(default="chrome", description="Header x-devicetype; accepted values: ios, android, chrome, opera, firefox, edge")
    NEO_REQUEST_TIMEOUT: float = Field(default=15.0, gt=0, description="Timeout request NeoAPI (giây)")
    NEO_RATE_LIMIT_RPS: float = Field(
        default=5.0,
        le=5.0,
        gt=0,
        description="Giới hạn tối đa số request/giây (NeoAPI quy định 5 req/s)",
    )

    # 2. Supplementary Data Source: SSI FastConnect API (Authorized Fallback)
    SSI_FASTCONNECT_URL: str = Field(
        default="https://api.ssi.com.vn",
        description="Base URL SSI FastConnect API"
    )
    SSI_IBOARD_URL: str = Field(
        default="https://iboard-query.ssi.com.vn",
        description="Endpoint dữ liệu thị trường trực tiếp SSI iBoard"
    )
    SSI_API_KEY: str = Field(default="", description="API Key SSI FastConnect (nếu có)")
    SSI_API_SECRET: str = Field(default="", description="API Secret SSI FastConnect (nếu có)")
    SSI_PRIVATE_KEY: str = Field(default="", description="Private Key SSI FastConnect (nếu có)")

    # 3. App Settings
    APP_ENV: str = Field(default="development", description="Môi trường ứng dụng")
    APP_PORT: int = Field(default=8501, description="Cổng chạy Streamlit")
    DATA_CACHE_DIR: str = Field(default="./data_sample", description="Thư mục cache dữ liệu")
    DEFAULT_UNIVERSE: str = Field(default="ALL", description="Phạm vi dữ liệu mặc định: ALL hoặc VN30")


# Singleton instance
settings = Settings()
