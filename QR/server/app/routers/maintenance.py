from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime

from app.database.connection import get_db
from app.models.user import User
from app.models.asset import Asset
from app.models.maintenance import Maintenance as MaintenanceModel
from app.schemas.maintenance import Maintenance, MaintenanceCreate, MaintenanceUpdate

router = APIRouter()

@router.get("/", response_model=List[Maintenance])
def read_maintenance_records(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    asset_id: Optional[int] = Query(None, description="Filter by asset id"),
) -> Any:
    try:
        stmt = select(MaintenanceModel)
        if asset_id is not None:
            stmt = stmt.where(MaintenanceModel.asset_id == asset_id)
        
        # 🟢 เรียงลำดับจากล่าสุดขึ้นก่อน จะได้เห็นรายการแจ้งซ่อมทันที
        stmt = stmt.order_by(MaintenanceModel.id.desc()).offset(skip).limit(limit)
        records = db.execute(stmt).scalars().all()
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

@router.post("/", response_model=Maintenance)
def create_maintenance(
    *,
    db: Session = Depends(get_db),
    maintenance_in: MaintenanceCreate,
) -> Any:
    try:
        # 1. ค้นหาด้วย Asset ID ก่อน
        stmt = select(Asset).where(Asset.id == maintenance_in.asset_id)
        asset = db.execute(stmt).scalar_one_or_none()

        # 2. ถ้าไม่เจอ ให้หาด้วย asset_code (รองรับทั้งเติม 0 สี่หลัก และสามหลัก)
        if not asset:
            code_str = str(maintenance_in.asset_id)
            stmt_code = select(Asset).where(
                (Asset.asset_code == code_str) | 
                (Asset.asset_code == code_str.zfill(4)) | 
                (Asset.asset_code == code_str.zfill(3))
            )
            asset = db.execute(stmt_code).scalar_one_or_none()

        if not asset:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลครุภัณฑ์ในระบบ")

        # 🟢 ปล่อย reporter_id เป็น None สำหรับคนทั่วไปที่สแกนจากมือถือ
        db_obj = MaintenanceModel(
            asset_id=asset.id,
            reporter_id=None,
            reporter_name=maintenance_in.reporter_name or "ประชาชนทั่วไป",
            issue_description=maintenance_in.issue_description,
            urgency=maintenance_in.urgency or "Normal",
            status="Pending",
            notes=maintenance_in.notes
        )
        db.add(db_obj)

        # อัปเดตสถานะของ Asset เป็นส่งซ่อม
        asset.status = "ส่งซ่อม"

        db.commit()
        db.refresh(db_obj)

        return db_obj

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.put("/{maintenance_id}", response_model=Maintenance)
def update_maintenance(
    *,
    db: Session = Depends(get_db),
    maintenance_id: int,
    maintenance_in: MaintenanceUpdate,
) -> Any:
    stmt = select(MaintenanceModel).where(MaintenanceModel.id == maintenance_id)
    record = db.execute(stmt).scalar_one_or_none()
    
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
        
    if maintenance_in.status in ["Done", "Returned", "ใช้งานได้ปกติ"]:
        maintenance_in.completed_at = datetime.utcnow()
        asset_stmt = select(Asset).where(Asset.id == record.asset_id)
        asset = db.execute(asset_stmt).scalar_one_or_none()
        if asset:
            asset.status = "ใช้งานได้ปกติ"
             
    for field, value in maintenance_in.dict(exclude_unset=True).items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record