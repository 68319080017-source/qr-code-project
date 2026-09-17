import os
import qrcode
from typing import List, Optional, Any
from datetime import datetime
import zoneinfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from pydantic import BaseModel

from app.database.connection import get_db
from app.models.asset import Asset
from app.models.maintenance import Maintenance as MaintenanceModel
from app.models.requisition import Requisition as RequisitionModel

router = APIRouter()

THAI_TZ = zoneinfo.ZoneInfo("Asia/Bangkok")

# =========================================================
# PYDANTIC SCHEMAS
# =========================================================
class AssetBase(BaseModel):
    asset_code: str
    name: str
    category: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
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

# 1. ดึงข้อมูลครุภัณฑ์ทั้งหมด (พร้อมตัวเลือกค้นหา)
@router.get("/", response_model=List[AssetResponse])
def get_all_assets(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 500,
    search: Optional[str] = Query(None, description="ค้นหาจากรหัส, ชื่อ หรือสถานที่"),
    status_filter: Optional[str] = Query(None, description="กรองตามสถานะ")
):
    query = db.query(Asset)

    if search:
        search_fmt = f"%{search}%"
        filter_conditions = [
            Asset.asset_code.ilike(search_fmt),
            Asset.name.ilike(search_fmt),
            Asset.category.ilike(search_fmt)
        ]
        
        # เช็กความปลอดภัย ป้องกัน Query พังถ้าคอลัมน์ไม่มีอยู่จริงใน DB Model
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

    # เติมค่า location ให้ Pydantic Response หากใน Model DB ใช้ชื่ออื่น
    for asset in assets:
        if not getattr(asset, "location", None):
            setattr(asset, "location", getattr(asset, "building", None) or getattr(asset, "department", None))

    return assets


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

    return asset


# 3. สรุปสถิติสำหรับ Dashboard
@router.get("/summary/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
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


# 4. Audit Log Timeline ดึงประวัติกิจกรรมของครุภัณฑ์
@router.get("/{asset_id}/timeline")
def get_asset_timeline(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลครุภัณฑ์")

    timeline_events = []

    # ประวัติการลงทะเบียน
    if hasattr(asset, 'created_at') and asset.created_at:
        timeline_events.append({
            "timestamp": asset.created_at.strftime("%d %b %Y - %H:%M น."),
            "action": "ลงทะเบียนครุภัณฑ์เข้าสู่ระบบ",
            "action_by": "System Admin",
            "details": f"สถานที่จัดเก็บ: {getattr(asset, 'building', None) or getattr(asset, 'department', None) or 'ไม่ระบุ'}",
            "type": "register"
        })

    # ประวัติการแจ้งซ่อม
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

    # ประวัติการเบิกจ่าย
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


# 5. เพิ่มครุภัณฑ์ใหม่ (ฉบับแก้ Schema Mismatch ชัวร์ 100%)
@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(asset_in: AssetCreate, db: Session = Depends(get_db)):
    existing = db.query(Asset).filter(Asset.asset_code == asset_in.asset_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="รหัสครุภัณฑ์นี้มีในระบบแล้ว")
    
    try:
        # 1. Gen QR Code
        qr_path = generate_qr_code(asset_in.asset_code)
        
        # 2. แปลง Pydantic เป็น Dict
        asset_dict = asset_in.model_dump() if hasattr(asset_in, "model_dump") else asset_in.dict()
        asset_dict["qr_code_path"] = qr_path
        
        # 3. ดึงค่า location ออกมาเตรียมไว้
        raw_location = asset_dict.pop("location", None)
        
        # 4. คัดกรองเอาเฉพาะ Key ที่มีชื่อตรงกับ คอลัมน์ ใน Table DB จริงเท่านั้น
        valid_columns = {c.name for c in Asset.__table__.columns}
        filtered_data = {k: v for k, v in asset_dict.items() if k in valid_columns}

        # แมปค่า location ไปยัง building หรือ department ถ้าตารางมีคอลัมน์นั้น
        if raw_location:
            if "location" in valid_columns:
                filtered_data["location"] = raw_location
            elif "building" in valid_columns and not filtered_data.get("building"):
                filtered_data["building"] = raw_location

        # 5. บันทึกข้อมูลลงฐานข้อมูล
        new_asset = Asset(**filtered_data)
        db.add(new_asset)
        db.commit()
        db.refresh(new_asset)
        
        # เติมค่า location กลับเข้าไปส่งให้ Response Model
        setattr(new_asset, "location", raw_location or getattr(new_asset, "building", None))
        return new_asset

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Database Server Error: {str(e)}"
        )


# 6. แก้ไขข้อมูลครุภัณฑ์
@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(asset_id: int, asset_in: AssetUpdate, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="ไม่พบรายการครุภัณฑ์")
    
    update_data = asset_in.model_dump() if hasattr(asset_in, "model_dump") else asset_in.dict()
    loc_val = update_data.pop("location", None)

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
    return asset


# 7. ลบข้อมูลครุภัณฑ์
@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="ไม่พบรายการครุภัณฑ์")
    
    db.delete(asset)
    db.commit()
    return None


# 8. สร้างตั๋วแจ้งซ่อมด่วน (Ticket)
@router.post("/maintenance/ticket")
def create_maintenance_ticket(item: MaintenanceCreateTicket, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == item.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="ไม่พบครุภัณฑ์")
    
    asset.status = "ส่งซ่อม"
    db.commit()
    return {"message": "บันทึกการแจ้งซ่อมเรียบร้อย"}