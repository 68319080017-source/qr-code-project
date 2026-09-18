import os
import qrcode
from typing import List, Optional, Any
from datetime import datetime
import zoneinfo

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from pydantic import BaseModel

import cloudinary
import cloudinary.uploader

from app.database.connection import get_db
from app.models.asset import Asset
from app.models.maintenance import Maintenance as MaintenanceModel
from app.models.requisition import Requisition as RequisitionModel

router = APIRouter()

THAI_TZ = zoneinfo.ZoneInfo("Asia/Bangkok")

# =========================================================
# CLOUDINARY CONFIG
# =========================================================
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# =========================================================
# PYDANTIC SCHEMAS
# =========================================================
class AssetBase(BaseModel):
    asset_code: Optional[str] = "-"
    name: Optional[str] = "-"
    category: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = "ใช้งานปกติ"
    price: Optional[float] = 0.0
    image_path: Optional[str] = None

class AssetCreate(AssetBase):
    pass

class AssetUpdate(AssetBase):
    pass

class AssetResponse(AssetBase):
    id: int
    qr_code_path: Optional[str] = None

    class Config:
        from_attributes = True

class MaintenanceCreateTicket(BaseModel):
    asset_id: int
    reporter_name: str
    description: str


# =========================================================
# HELPER FUNCTION: GENERATE QR CODE IMAGE
# =========================================================
def generate_qr_code(asset_code: str) -> str:
    """สร้างไฟล์รูปภาพ QR Code โดยใช้ Absolute Path"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        folder = os.path.normpath(os.path.join(base_dir, "..", "static", "qrcodes"))
        os.makedirs(folder, exist_ok=True)
        
        filename = f"{asset_code}.png"
        filepath = os.path.join(folder, filename)
        
        img = qrcode.make(asset_code)
        img.save(filepath)
        return f"/static/qrcodes/{filename}"
    except Exception:
        return ""


# =========================================================
# ENDPOINTS
# =========================================================

# 1. ดึงข้อมูลครุภัณฑ์ทั้งหมด
@router.get("/", response_model=List[AssetResponse])
def get_all_assets(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 500,
    search: Optional[str] = Query(None, description="ค้นหาจากรหัส, ชื่อ หรือสถานที่"),
    status_filter: Optional[str] = Query(None, description="กรองตามสถานะ")
):
    try:
        query = db.query(Asset)

        if search:
            search_fmt = f"%{search}%"
            filter_conditions = [
                Asset.asset_code.ilike(search_fmt),
                Asset.name.ilike(search_fmt),
                Asset.category.ilike(search_fmt)
            ]
            
            if hasattr(Asset, "building"):
                filter_conditions.append(Asset.building.ilike(search_fmt))
            if hasattr(Asset, "room"):
                filter_conditions.append(Asset.room.ilike(search_fmt))
            if hasattr(Asset, "department"):
                filter_conditions.append(Asset.department.ilike(search_fmt))

            query = query.filter(or_(*filter_conditions))

        if status_filter:
            query = query.filter(Asset.status == status_filter)

        assets = query.order_by(Asset.id.desc()).offset(skip).limit(limit).all()

        for asset in assets:
            if not getattr(asset, "location", None):
                setattr(asset, "location", getattr(asset, "building", None) or getattr(asset, "department", None))
            
            img_val = getattr(asset, "image_path", None) or getattr(asset, "image_url", None) or getattr(asset, "image", None)
            setattr(asset, "image_path", img_val)

        return assets
    except Exception as e:
        print(f"[Get Assets Error]: {e}")
        return []


# 2. ค้นหาครุภัณฑ์ผ่านรหัส QR Code
@router.get("/code/{asset_code}", response_model=AssetResponse)
def get_asset_by_code(asset_code: str, db: Session = Depends(get_db)):
    code_str = str(asset_code).strip()
    
    asset = db.query(Asset).filter(
        or_(
            Asset.asset_code == code_str,
            Asset.asset_code == code_str.zfill(4),
            Asset.asset_code == code_str.zfill(3)
        )
    ).first()

    if not asset:
        raise HTTPException(status_code=404, detail=f"ไม่พบข้อมูลครุภัณฑ์รหัส '{asset_code}' ในระบบ")
    
    if not getattr(asset, "location", None):
        setattr(asset, "location", getattr(asset, "building", None) or getattr(asset, "department", None))

    img_val = getattr(asset, "image_path", None) or getattr(asset, "image_url", None) or getattr(asset, "image", None)
    setattr(asset, "image_path", img_val)

    return asset


# 3. สรุปสถิติสำหรับ Dashboard
@router.get("/summary/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    try:
        return {
            "total": db.query(Asset).count(),
            "normal": db.query(Asset).filter(
                or_(Asset.status == "ใช้งานปกติ", Asset.status == "ใช้งานได้ปกติ", Asset.status == "Ready")
            ).count(),
            "withdrawn": db.query(Asset).filter(Asset.status == "ถูกเบิกออก").count(),
            "maintenance": db.query(Asset).filter(
                or_(Asset.status == "ส่งซ่อม", Asset.status == "Under Repair")
            ).count(),
            "retired": db.query(Asset).filter(
                or_(
                    Asset.status == "ชำรุด/จำหน่าย", 
                    Asset.status == "ชำรุด/แทงจำหน่าย",
                    Asset.status == "แทงจำหน่าย"
                )
            ).count()
        }
    except Exception as e:
        print(f"[Dashboard Stats Error]: {e}")
        return {"total": 0, "normal": 0, "withdrawn": 0, "maintenance": 0, "retired": 0}


# 4. Audit Log Timeline ดึงประวัติกิจกรรมของครุภัณฑ์
@router.get("/{asset_id}/timeline")
def get_asset_timeline(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลครุภัณฑ์")

    timeline_events = []

    if hasattr(asset, 'created_at') and asset.created_at:
        timeline_events.append({
            "timestamp": asset.created_at.strftime("%d %b %Y - %H:%M น."),
            "action": "ลงทะเบียนครุภัณฑ์เข้าสู่ระบบ",
            "action_by": "System Admin",
            "details": f"สถานที่จัดเก็บ: {getattr(asset, 'building', None) or getattr(asset, 'department', None) or 'ไม่ระบุ'}",
            "type": "register"
        })

    try:
        maint_records = db.query(MaintenanceModel).filter(MaintenanceModel.asset_id == asset_id).order_by(MaintenanceModel.id.desc()).all()
        for m in maint_records:
            t_str = m.created_at.strftime("%d %b %Y - %H:%M น.") if hasattr(m, 'created_at') and m.created_at else "ไม่ระบุเวลา"
            timeline_events.append({
                "timestamp": t_str,
                "action": f"แจ้งซ่อม (สถานะ: {m.status})",
                "action_by": getattr(m, 'reporter_name', 'ประชาชนทั่วไป'),
                "details": f"อาการเสีย: {getattr(m, 'issue_description', '-')}",
                "type": "maintenance"
            })
    except Exception:
        pass

    try:
        req_records = db.query(RequisitionModel).filter(RequisitionModel.asset_id == asset_id).order_by(RequisitionModel.id.desc()).all()
        for r in req_records:
            t_str = r.created_at.strftime("%d %b %Y - %H:%M น.") if hasattr(r, 'created_at') and r.created_at else "ไม่ระบุเวลา"
            timeline_events.append({
                "timestamp": t_str,
                "action": f"ขอเบิกอุปกรณ์ (สถานะ: {r.status})",
                "action_by": getattr(r, 'requester_name', 'ผู้ใช้งาน'),
                "details": f"วัตถุประสงค์: {getattr(r, 'purpose', '-')}",
                "type": "requisition"
            })
    except Exception:
        pass

    return {
        "asset_code": asset.asset_code,
        "asset_name": asset.name,
        "current_status": asset.status,
        "timeline": timeline_events
    }


# 5. เพิ่มครุภัณฑ์ใหม่ (แก้ไขให้รองรับ Form Data และอัปโหลดไฟล์รูปภาพ)
@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_code: str = Form(...),
    name: str = Form(...),
    category: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    asset_status: Optional[str] = Form("ใช้งานปกติ", alias="status"),
    price: Optional[float] = Form(0.0),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    existing = db.query(Asset).filter(Asset.asset_code == asset_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="รหัสครุภัณฑ์นี้มีในระบบแล้ว")
    
    try:
        # สร้าง QR Code
        qr_path = generate_qr_code(asset_code)
        
        # อัปโหลดรูปภาพไปยัง Cloudinary (ถ้ามีส่งไฟล์มา)
        image_url = None
        if file and file.filename:
            try:
                result = cloudinary.uploader.upload(file.file, folder="asset_photos")
                image_url = result.get("secure_url")
            except Exception as upload_err:
                print(f"[Cloudinary Upload Error]: {upload_err}")

        valid_columns = {c.name for c in Asset.__table__.columns}
        
        asset_dict = {
            "asset_code": asset_code,
            "name": name,
            "category": category,
            "department": department,
            "status": asset_status,
            "price": price,
            "qr_code_path": qr_path
        }

        if location:
            if "location" in valid_columns:
                asset_dict["location"] = location
            elif "building" in valid_columns:
                asset_dict["building"] = location

        if image_url:
            if "image_path" in valid_columns:
                asset_dict["image_path"] = image_url
            if "image_url" in valid_columns:
                asset_dict["image_url"] = image_url
            if "image" in valid_columns:
                asset_dict["image"] = image_url

        filtered_data = {k: v for k, v in asset_dict.items() if k in valid_columns}

        new_asset = Asset(**filtered_data)
        db.add(new_asset)
        db.commit()
        db.refresh(new_asset)
        
        setattr(new_asset, "location", location or getattr(new_asset, "building", None))
        setattr(new_asset, "image_path", image_url)
        return new_asset

    except Exception as e:
        db.rollback()
        print(f"[Create Asset Error]: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database Server Error: {str(e)}"
        )


# 6. อัปโหลดรูปภาพครุภัณฑ์ขึ้น Cloudinary ถาวร
@router.post("/{asset_id}/upload-image")
async def upload_asset_image(
    asset_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="ไม่พบรายการครุภัณฑ์")

    try:
        result = cloudinary.uploader.upload(file.file, folder="asset_photos")
        image_url = result.get("secure_url")

        valid_columns = {c.name for c in Asset.__table__.columns}
        if "image_path" in valid_columns:
            asset.image_path = image_url
        if "image_url" in valid_columns:
            asset.image_url = image_url
        if "image" in valid_columns:
            asset.image = image_url

        db.commit()
        db.refresh(asset)
        return {"message": "อัปโหลดรูปภาพสำเร็จ", "image_url": image_url}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload Error: {str(e)}")


# 7. แก้ไขข้อมูลครุภัณฑ์
@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(asset_id: int, asset_in: AssetUpdate, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="ไม่พบรายการครุภัณฑ์")
    
    update_data = asset_in.model_dump() if hasattr(asset_in, "model_dump") else asset_in.dict()
    loc_val = update_data.pop("location", None)
    update_data.pop("image_path", None)

    valid_columns = {c.name for c in Asset.__table__.columns}
    
    if loc_val:
        if "location" in valid_columns:
            update_data["location"] = loc_val
        elif "building" in valid_columns:
            update_data["building"] = loc_val

    for key, value in update_data.items():
        if key in valid_columns and hasattr(asset, key):
            setattr(asset, key, value)
        
    db.commit()
    db.refresh(asset)
    setattr(asset, "location", loc_val or getattr(asset, "building", None))
    img_val = getattr(asset, "image_path", None) or getattr(asset, "image_url", None) or getattr(asset, "image", None)
    setattr(asset, "image_path", img_val)
    return asset


# 8. ลบข้อมูลครุภัณฑ์
@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="ไม่พบรายการครุภัณฑ์")
    
    db.delete(asset)
    db.commit()
    return None


# 9. สร้างตั๋วแจ้งซ่อมด่วน (Ticket)
@router.post("/maintenance/ticket")
def create_maintenance_ticket(item: MaintenanceCreateTicket, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == item.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="ไม่พบครุภัณฑ์")
    
    asset.status = "ส่งซ่อม"
    db.commit()
    return {"message": "บันทึกการแจ้งซ่อมเรียบร้อย"}