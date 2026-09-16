"""
Configuration Settings
Application configuration using Pydantic Settings
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    # Database Configuration
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="qr_assets", alias="DB_NAME")
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: str = Field(default="postgres", alias="DB_PASSWORD")
    
    # Security Configuration
    secret_key: str = Field(..., alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_minutes: int = Field(default=43200, alias="REFRESH_TOKEN_EXPIRE_MINUTES")
    
    # Application Configuration
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    
    # Redis Configuration
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    
    # QR Code Configuration
    qr_code_size: int = Field(default=300, alias="QR_CODE_SIZE")
    qr_code_border: int = Field(default=4, alias="QR_CODE_BORDER")
    qr_code_format: str = Field(default="png", alias="QR_CODE_FORMAT")
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:8000", "http://localhost:3000", "https://localhost:8000"],
        alias="CORS_ORIGINS"
    )
    
    # Allowed hosts for TrustedHostMiddleware
    allowed_hosts: List[str] = Field(
        default=["*"],
        alias="ALLOWED_HOSTS"
    )
    
    # Pagination Configuration
    default_page_size: int = Field(default=20, alias="DEFAULT_PAGE_SIZE")
    max_page_size: int = Field(default=100, alias="MAX_PAGE_SIZE")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, alias="RATE_LIMIT_WINDOW")
    
    # Audit Logging
    audit_log_enabled: bool = Field(default=True, alias="AUDIT_LOG_ENABLED")
    audit_log_level: str = Field(default="INFO", alias="AUDIT_LOG_LEVEL")
    
    # External Services
    alchemy_api_key: Optional[str] = Field(default=None, alias="ALCHEMY_API_KEY")
    
    # Database URL (computed property)
    @property
    def database_url(self) -> str:
        """Construct database URL from components"""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
    
    # Redis URL (computed property)
    @property
    def redis_url(self) -> str:
        """Construct Redis URL from components"""
        password = f":{self.redis_password}" if self.redis_password else ""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


# Create settings instance
settings = Settings()