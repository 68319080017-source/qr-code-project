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
        
        stmt = stmt.offset(skip).limit(limit)
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
        stmt = select(Asset).where(Asset.id == maintenance_in.asset_id)
        asset = db.execute(stmt).scalar_one_or_none()

        if not asset:
            stmt_code = select(Asset).where(Asset.asset_code == str(maintenance_in.asset_id).zfill(3))
            asset = db.execute(stmt_code).scalar_one_or_none()

        if not asset:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลครุภัณฑ์ในระบบ")

        # 🟢 ถ้ามี User ในระบบค่อยดึง id มาใช้ ถ้าไม่มีให้เป็น None (ไม่ใส่เลข 1 เพื่อแก้ปัญหา ForeignKeyViolation)
        default_user = db.execute(select(User)).scalars().first()
        reporter_id = default_user.id if default_user else None

        db_obj = MaintenanceModel(
            asset_id=asset.id,
            reporter_id=reporter_id,
            reporter_name=maintenance_in.reporter_name or "ประชาชนทั่วไป",
            issue_description=maintenance_in.issue_description,
            urgency=maintenance_in.urgency or "Normal",
            status="Pending",
            notes=maintenance_in.notes
        )
        db.add(db_obj)

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