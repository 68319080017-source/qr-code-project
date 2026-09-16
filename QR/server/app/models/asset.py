from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text
from sqlalchemy.sql import func
from app.models.base import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False, index=True)
    category = Column(String, index=True)
    brand = Column(String)
    model = Column(String)
    serial_number = Column(String, index=True)
    price = Column(Float, default=0.0)
    purchase_date = Column(Date)
    building = Column(String, index=True)
    room = Column(String, index=True)
    department = Column(String)
    responsible_person = Column(String, index=True)
    status = Column(String, default="Normal") # Normal, Broken, Repairing, Sold
    notes = Column(Text)
    image_path = Column(String)
    qr_code_path = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
