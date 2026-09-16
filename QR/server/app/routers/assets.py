import os
import qrcode
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.connection import get_db
from app.models.asset import Asset

router = APIRouter()

# --- Pydantic Schemas ---
class AssetBase(BaseModel):
    asset_code: str
    name: str
    category: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = "ใช้งานปกติ"
    price: Optional[float] = 0.0

class AssetCreate(AssetBase):
    pass

class AssetUpdate(AssetBase):
    pass

class AssetResponse(AssetBase):
    id: int
    qr_code_path: Optional[str] = None

    class Config:
        from_attributes = True

class MaintenanceCreate(BaseModel):
    asset_id: int
    reporter_name: str
    description: str

# --- Helper Function: Gen QR Code ---
def generate_qr_code(asset_code: str) -> str:
    folder = "app/static/qrcodes"
    os.makedirs(folder, exist_ok=True)
    filename = f"{asset_code}.png"
    filepath = os.path.join(folder, filename)
    
    img = qrcode.make(asset_code)
    img.save(filepath)
    return f"/static/qrcodes/{filename}"

# --- Endpoints ---
@router.get("/", response_model=List[AssetResponse])
def get_all_assets(db: Session = Depends(get_db)):
    return db.query(Asset).all()

@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(asset_in: AssetCreate, db: Session = Depends(get_db)):
    existing = db.query(Asset).filter(Asset.asset_code == asset_in.asset_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="รหัสครุภัณฑ์นี้มีในระบบแล้ว")
    
    qr_path = generate_qr_code(asset_in.asset_code)
    new_asset = Asset(**asset_in.dict(), qr_code_path=qr_path)
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)
    return new_asset

@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(asset_id: int, asset_in: AssetUpdate, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="ไม่พบรายการครุภัณฑ์")
    
    for key, value in asset_in.dict().items():
        setattr(asset, key, value)
        
    db.commit()
    db.refresh(asset)
    return asset

@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="ไม่พบรายการครุภัณฑ์")
    
    db.delete(asset)
    db.commit()
    return None

# 🟢 เพิ่มการดึงค่า status "ถูกเบิกออก" เพื่อส่งไปยัง Dashboard
@router.get("/summary/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    return {
        "total": db.query(Asset).count(),
        "normal": db.query(Asset).filter(Asset.status == "ใช้งานปกติ").count(),
        "withdrawn": db.query(Asset).filter(Asset.status == "ถูกเบิกออก").count(),
        "maintenance": db.query(Asset).filter(Asset.status == "ส่งซ่อม").count(),
        "retired": db.query(Asset).filter((Asset.status == "ชำรุด/จำหน่าย") | (Asset.status == "ชำรุด/แทงจำหน่าย")).count()
    }

@router.post("/maintenance/ticket")
def create_maintenance_ticket(item: MaintenanceCreate, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == item.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="ไม่พบครุภัณฑ์")
    
    asset.status = "ส่งซ่อม"
    db.commit()
    return {"message": "บันทึกการแจ้งซ่อมเรียบร้อย"}