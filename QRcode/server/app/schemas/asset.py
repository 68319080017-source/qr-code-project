from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime

class AssetBase(BaseModel):
    asset_number: str
    name: str
    description: Optional[str] = None

    category_id: Optional[UUID] = None
    asset_type: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None

    manufacturer: Optional[str] = None
    vendor: Optional[str] = None

    purchase_date: Optional[date] = None
    receive_date: Optional[date] = None
    warranty_expire_date: Optional[date] = None
    price: Optional[float] = None
    budget_source: Optional[str] = None
    fiscal_year: Optional[str] = None

    location_id: Optional[UUID] = None
    position_details: Optional[str] = None

    department: Optional[str] = None
    responsible_user_id: Optional[UUID] = None

    status: str = "ปกติ"
    notes: Optional[str] = None

class AssetCreate(AssetBase):
    pass

class AssetUpdate(AssetBase):
    asset_number: Optional[str] = None
    name: Optional[str] = None

class Asset(AssetBase):
    id: UUID
    asset_code: Optional[str] = None
    qr_code_id: Optional[str] = None
    image_url: Optional[str] = None
    attachments: Optional[str] = "[]"
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
