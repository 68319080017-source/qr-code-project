from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

# Maintenance Log Schemas
class MaintenanceLogBase(BaseModel):
    issue_description: str
    status: str = "รอซ่อม"
    cost: Optional[float] = 0.0

class MaintenanceLogCreate(MaintenanceLogBase):
    asset_number: str

class MaintenanceLog(MaintenanceLogBase):
    id: UUID
    asset_id: UUID
    reported_by_id: Optional[UUID] = None
    before_image_url: Optional[str] = None
    after_image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Audit Log Schemas
class AuditLogBase(BaseModel):
    status: str = "ปกติ"
    notes: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    asset_number: str

class AuditLog(AuditLogBase):
    id: UUID
    asset_id: UUID
    auditor_id: Optional[UUID] = None
    location_verified: bool = True
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
