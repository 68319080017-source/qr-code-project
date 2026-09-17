import os
import requests
import zoneinfo
from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.connection import get_db
from app.models.user import User
from app.models.asset import Asset
from app.models.maintenance import Maintenance as MaintenanceModel
from app.schemas.maintenance import Maintenance, MaintenanceCreate, MaintenanceUpdate

router = APIRouter()

THAI_TZ = zoneinfo.ZoneInfo("Asia/Bangkok")

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
LINE_USER_OR_GROUP_ID = os.getenv("LINE_USER_OR_GROUP_ID", "")


def send_line_maintenance_notification(asset_code: str, asset_name: str, reporter_name: str, urgency: str, issue: str):
    """ส่งข้อความแจ้งเตือนผ่าน LINE Push Message"""
    if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_USER_OR_GROUP_ID:
        return

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    
    msg_text = (
        f"⚠️ [แจ้งซ่อมครุภัณฑ์ใหม่]\n"
        f"📌 รหัส: {asset_code}\n"
        f"📦 ครุภัณฑ์: {asset_name}\n"
        f"👤 ผู้แจ้ง: {reporter_name}\n"
        f"🚨 ความเร่งด่วน: {urgency}\n"
        f"💬 อาการเสีย: {issue}"
    )

    payload = {
        "to": LINE_USER_OR_GROUP_ID,
        "messages": [{"type": "text", "text": msg_text}]
    }

    try:
        requests.post(url, headers=headers, json=payload, timeout=5)
    except Exception as e:
        print(f"[LINE Notify Error]: {e}")


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
    background_tasks: BackgroundTasks
) -> Any:
    try:
        # 1. ค้นหาด้วย Asset ID ก่อน
        stmt = select(Asset).where(Asset.id == maintenance_in.asset_id)
        asset = db.execute(stmt).scalar_one_or_none()

        # 2. ถ้าไม่เจอ ให้หาด้วย asset_code
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

        reporter_name = maintenance_in.reporter_name or "ประชาชนทั่วไป"
        urgency = maintenance_in.urgency or "Normal"

        db_obj = MaintenanceModel(
            asset_id=asset.id,
            reporter_id=None,
            reporter_name=reporter_name,
            issue_description=maintenance_in.issue_description,
            urgency=urgency,
            status="Pending",
            notes=maintenance_in.notes
        )
        db.add(db_obj)

        # อัปเดตสถานะของ Asset
        asset.status = "ส่งซ่อม"

        db.commit()
        db.refresh(db_obj)

        # ส่ง LINE Notification ในรูปแบบ Background Task
        background_tasks.add_task(
            send_line_maintenance_notification,
            asset_code=asset.asset_code,
            asset_name=asset.name,
            reporter_name=reporter_name,
            urgency=urgency,
            issue=maintenance_in.issue_description
        )

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
        
    if maintenance_in.status in ["Done", "Returned", "ใช้งานได้ปกติ", "Completed"]:
        maintenance_in.completed_at = datetime.now(THAI_TZ)
        asset_stmt = select(Asset).where(Asset.id == record.asset_id)
        asset = db.execute(asset_stmt).scalar_one_or_none()
        if asset:
            asset.status = "ใช้งานได้ปกติ"
             
    for field, value in maintenance_in.dict(exclude_unset=True).items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record