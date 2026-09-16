from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.connection import get_db
from app.models.asset import Asset
from app.models.requisition import Requisition
from app.schemas.requisition import RequisitionCreate, RequisitionResponse

router = APIRouter()

@router.get("/", response_model=List[RequisitionResponse])
def get_requisitions(db: Session = Depends(get_db)) -> Any:
    stmt = select(Requisition).order_by(Requisition.id.desc())
    return db.execute(stmt).scalars().all()

@router.post("/", response_model=RequisitionResponse)
def create_requisition(req_in: RequisitionCreate, db: Session = Depends(get_db)) -> Any:
    stmt = select(Asset).where(Asset.id == req_in.asset_id)
    asset = db.execute(stmt).scalar_one_or_none()
    
    if not asset:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลครุภัณฑ์ในระบบ")

    # เปลี่ยนสถานะ Asset เป็นถูกเบิกออก
    asset.status = "ถูกเบิกออก"

    req_obj = Requisition(
        asset_id=asset.id,
        requester_name=req_in.requester_name,
        department=req_in.department,
        purpose=req_in.purpose
    )
    
    db.add(req_obj)
    db.commit()
    db.refresh(req_obj)
    return req_obj