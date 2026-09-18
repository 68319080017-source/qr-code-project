import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# ดึง DATABASE_URL จาก Environment Variable บน Render
DATABASE_URL = os.getenv("DATABASE_URL", settings.SQLALCHEMY_DATABASE_URI)

# แปลง prefix postgres:// เป็น postgresql:// เพื่อรองรับ SQLAlchemy v2
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# แยกการตั้งค่า Engine ระหว่าง SQLite ( Local ) และ PostgreSQL ( Cloud )
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,   # ตรวจสอบความพร้อมของ Connection ก่อนยิง Query
        pool_recycle=300,     # คืน Connection ทุก 5 นาที ป้องกันการค้าง
        pool_size=5,          # จำกัดจำนวน Connection หลักไว้ที่ 5
        max_overflow=10       # สำรอง Connection เพิ่มชั่วคราวได้อีก 10
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()