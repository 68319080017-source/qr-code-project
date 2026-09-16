from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class MaintenanceBase(BaseModel):
    asset_id: int
    reporter_name: Optional[str] = "ไม่ระบุชื่อ"
    issue_description: str
    urgency: Optional[str] = "Normal"
    status: Optional[str] = "Pending"
    notes: Optional[str] = None

class MaintenanceCreate(MaintenanceBase):
    pass

class MaintenanceUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None

class Maintenance(MaintenanceBase):
    id: int
    reporter_id: int
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True