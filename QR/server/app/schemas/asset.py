from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

# Schema พื้นฐานสำหรับข้อมูลครุภัณฑ์
class AssetBase(BaseModel):
    asset_code: str
    name: str
    category: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = "active"
    price: Optional[float] = None

# Schema สำหรับสร้างครุภัณฑ์ใหม่ (รับค่าจาก Request)
class AssetCreate(AssetBase):
    pass

# Schema สำหรับแก้ไขข้อมูลครุภัณฑ์
class AssetUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    price: Optional[float] = None

# Schema สำหรับส่งข้อมูลออก (Response)
class AssetOut(AssetBase):
    id: int
    qr_code_path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)