from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Nullable for system actions or failed logins
    action = Column(String, nullable=False) # e.g., 'LOGIN', 'CREATE_ASSET', 'UPDATE_ASSET'
    target_entity = Column(String) # e.g., 'Asset: 123', 'User: admin'
    details = Column(Text)
    ip_address = Column(String)
    browser = Column(String)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="activity_logs")
