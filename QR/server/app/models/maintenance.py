from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base

def get_thai_time():
    return datetime.now(timezone(timedelta(hours=7)))

class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reporter_name = Column(String, nullable=True)
    issue_description = Column(Text, nullable=False)
    urgency = Column(String, default="Normal")
    status = Column(String, default="Pending")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_thai_time)

    # Relationships
    asset = relationship("Asset")
    reporter = relationship("User")