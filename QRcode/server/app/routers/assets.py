from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import uuid
import logging

from app.database.session import get_db
from app.models.asset import Asset as AssetModel
from app.schemas.asset import Asset, AssetCreate, AssetUpdate
from app.routers.deps import get_current_active_user
from app.services.qr_service import generate_qr_code
from app.services.excel_service import export_assets_to_excel
from app.services.pdf_service import export_assets_to_pdf

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[Asset])
def read_assets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    try:
        assets = db.query(AssetModel).offset(skip).limit(limit).all()
        return assets
    except Exception as e:
        logger.warning(f"Failed to query assets: {e}")
        return []

@router.post("/", response_model=Asset)
def create_asset(
    asset_in: AssetCreate,
    db: Session = Depends(get_db),
):
    asset_exists = db.query(AssetModel).filter(AssetModel.asset_number == asset_in.asset_number).first()
    if asset_exists:
        raise HTTPException(status_code=400, detail="Asset number already exists")
    
    # Generate UUID for QR Code tracking
    qr_code_id = str(uuid.uuid4())
    
    asset = AssetModel(
        **asset_in.model_dump(),
        qr_code_id=qr_code_id
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    
    # Generate QR Code image and save to disk
    generate_qr_code(qr_code_id)
    
    return asset

@router.get("/export/excel")
def export_excel(db: Session = Depends(get_db)):
    try:
        assets = db.query(AssetModel).all()
    except Exception as e:
        logger.warning(f"Failed to query assets for Excel export: {e}")
        assets = []
        
    file_stream = export_assets_to_excel(assets)
    
    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=assets_export.xlsx"}
    )

@router.get("/export/pdf")
def export_pdf(db: Session = Depends(get_db)):
    try:
        assets = db.query(AssetModel).all()
    except Exception as e:
        logger.warning(f"Failed to query assets for PDF export: {e}")
        assets = []
        
    file_stream = export_assets_to_pdf(assets)
    
    return StreamingResponse(
        file_stream,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=assets_report.pdf"}
    )
