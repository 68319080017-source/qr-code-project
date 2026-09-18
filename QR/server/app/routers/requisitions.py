from typing import Any, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.connection import get_db
from app.models.asset import Asset
from app.models.requisition import Requisition
from app.schemas.requisition import RequisitionCreate, RequisitionResponse

router = APIRouter()

# =========================================================
# 1. API ดึงรายการการเบิกอุปกรณ์ทั้งหมด
# =========================================================
@router.get("/", response_model=List[RequisitionResponse])
def get_requisitions(db: Session = Depends(get_db)) -> Any:
    try:
        stmt = select(Requisition).order_by(Requisition.id.desc())
        records = db.execute(stmt).scalars().all()
        return records
    except Exception as e:
        print(f"[Requisitions Fetch Error]: {str(e)}")
        # คืนค่า list ว่างแทนที่จะโยน Error 500 ออกไป ป้องกันหน้าเว็บหมุนค้าง
        return []


# =========================================================
# 2. API บันทึกการเบิกอุปกรณ์
# =========================================================
@router.post("/", response_model=RequisitionResponse, status_code=status.HTTP_201_CREATED)
def create_requisition(req_in: RequisitionCreate, db: Session = Depends(get_db)) -> Any:
    # 1. ค้นหา Asset
    stmt = select(Asset).where(Asset.id == req_in.asset_id)
    asset = db.execute(stmt).scalar_one_or_none()
    
    if not asset:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลครุภัณฑ์ในระบบ")

    # 2. ตรวจสอบสถานะว่าถูกเบิกไปแล้วหรือยัง
    if asset.status == "ถูกเบิกออก":
        raise HTTPException(status_code=400, detail="ครุภัณฑ์นี้ถูกเบิกออกไปแล้ว")

    try:
        # 3. เปลี่ยนสถานะ Asset
        asset.status = "ถูกเบิกออก"

        # 4. สร้างวัตถุ Requisition
        req_obj = Requisition(
            asset_id=asset.id,
            requester_name=req_in.requester_name,
            department=req_in.department,
            purpose=req_in.purpose or "เบิกใช้งานทั่วไป",
            created_at=datetime.now() # ใส่วันที่ปัจจุบันป้องกัน created_at เป็น None
        )
        
        db.add(req_obj)
        db.commit()
        db.refresh(req_obj)
        return req_obj

    except Exception as e:
        db.rollback() # ย้อนกลับ Transaction ถ้ามีปัญหา
        print(f"Database/Post Error: {str(e)}") # แสดงข้อมูล Error ใน Terminal
        raise HTTPException(
            status_code=500, 
            detail=f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {str(e)}"
        )