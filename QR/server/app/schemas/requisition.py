from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class RequisitionCreate(BaseModel):
    asset_id: int
    requester_name: str
    department: str
    purpose: Optional[str] = "เบิกใช้งานทั่วไป"

class RequisitionResponse(BaseModel):
    id: int
    asset_id: int
    requester_name: str
    department: str
    purpose: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True