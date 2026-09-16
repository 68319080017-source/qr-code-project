from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base

def get_thai_time():
    return datetime.now(timezone(timedelta(hours=7)))

class Requisition(Base):
    __tablename__ = "requisitions"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    requester_name = Column(String, nullable=False)     # ชื่อผู้เบิก
    department = Column(String, nullable=False)         # แผนก / สาขาวิชา
    purpose = Column(Text, nullable=True)               # วัตถุประสงค์การเบิก
    created_at = Column(DateTime, default=get_thai_time) # วันเวลาที่เบิก

    asset = relationship("Asset")