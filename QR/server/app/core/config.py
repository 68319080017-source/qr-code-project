from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "QR Code Asset Management System"
    API_V1_STR: str = "/api/v1"
    
    # Database Settings (เปลี่ยนมาใช้ SQLite)
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.DATABASE_URL
    
    @property
    def SQLALCHEMY_DATABASE_URI_SYNC(self) -> str:
        return self.DATABASE_URL

    # JWT Authentication
    SECRET_KEY: str = "super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 days

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()