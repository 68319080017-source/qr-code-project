from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.models.logs import AuditLog as AuditModel
from app.models.asset import Asset as AssetModel
from app.schemas.logs import AuditLog, AuditLogCreate
from app.routers.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[AuditLog])
def read_audit_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(AuditModel).offset(skip).limit(limit).all()

@router.post("/", response_model=AuditLog)
def create_audit_log(
    log_in: AuditLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify asset exists by asset_number
    asset = db.query(AssetModel).filter(AssetModel.asset_number == log_in.asset_number).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    # Extract dump without asset_number
    log_data = log_in.model_dump(exclude={'asset_number'})
        
    log = AuditModel(
        **log_data,
        asset_id=asset.id,
        auditor_id=current_user.id
    )
    db.add(log)
    
    # Update asset status
    asset.status = log_in.status
    
    db.commit()
    db.refresh(log)
    return log
