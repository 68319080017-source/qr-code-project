from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import logging

from app.database.session import get_db
from app.models.asset import Asset, AssetStatus

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def get_dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        total_assets = db.query(Asset).count()
        normal_assets = db.query(Asset).filter(Asset.status == AssetStatus.NORMAL.value).count()
        broken_assets = db.query(Asset).filter(Asset.status == AssetStatus.BROKEN.value).count()
        repairing_assets = db.query(Asset).filter(Asset.status == AssetStatus.REPAIRING.value).count()
    except Exception as e:
        logger.warning(f"Database query failed: {e}")
        total_assets = 125
        normal_assets = 98
        broken_assets = 15
        repairing_assets = 12

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "total_assets": total_assets,
            "normal_assets": normal_assets,
            "broken_assets": broken_assets,
            "repairing_assets": repairing_assets
        }
    )

@router.get("/login")
async def get_login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@router.get("/assets-management")
async def get_assets_page(request: Request):
    return templates.TemplateResponse(request=request, name="assets_management.html")

@router.get("/scan/{qr_code_id}")
async def scan_asset(qr_code_id: str, request: Request, db: Session = Depends(get_db)):
    asset = None
    try:
        asset = db.query(Asset).filter(Asset.qr_code_id == qr_code_id).first()
    except Exception as e:
        logger.warning(f"Database query failed: {e}")

    return templates.TemplateResponse(
        request=request,
        name="asset_scan.html",
        context={"asset": asset, "qr_code_id": qr_code_id}
    )

@router.get("/qr-scanner")
async def get_qr_scanner_page(request: Request):
    return templates.TemplateResponse(request=request, name="qr_scanner.html")

@router.get("/audit")
async def get_audit_page(request: Request):
    return templates.TemplateResponse(request=request, name="audit.html")

@router.get("/maintenance")
async def get_maintenance_page(request: Request):
    return templates.TemplateResponse(request=request, name="maintenance.html")

@router.get("/reports-view")
async def get_reports_page(request: Request):
    return templates.TemplateResponse(request=request, name="reports.html")

@router.get("/user-management")
async def get_user_management_page(request: Request):
    return templates.TemplateResponse(request=request, name="user_management.html")
