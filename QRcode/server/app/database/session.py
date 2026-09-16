from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

_use_sqlite = False
try:
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 1}
    )
    with engine.connect() as conn:
        pass
    logger.info("Connected to PostgreSQL.")
except Exception as e:
    logger.warning(f"PostgreSQL unavailable. Using SQLite fallback.")
    _use_sqlite = True
    engine = create_engine(
        "sqlite:///./qr_asset_management.db",
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
