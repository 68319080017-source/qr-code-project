from typing import Any, Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.models.user import User
from app.repositories.asset_repo import AssetRepository
from app.auth.dependencies import get_current_active_user, RoleChecker
from app.services.report_service import ReportService

router = APIRouter()
allow_view_reports = RoleChecker(["Super Admin", "Admin", "ผู้ตรวจสอบ", "เจ้าหน้าที่พัสดุ"])

@router.get("/assets/excel")
async def export_assets_excel(
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by status (Normal, Broken, etc)"),
    current_user: User = Depends(allow_view_reports),
) -> Any:
    """
    Export assets to Excel.
    """
    repo = AssetRepository(db)
    # Using a large limit for report generation, ideally we'd stream it or have background jobs
    assets = await repo.get_multi(limit=10000)
    if status:
        assets = [a for a in assets if a.status == status]
        
    filepath = ReportService.generate_excel_report(assets)
    return FileResponse(path=filepath, filename="assets_report.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@router.get("/assets/pdf")
async def export_assets_pdf(
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(allow_view_reports),
) -> Any:
    """
    Export assets to PDF.
    """
    repo = AssetRepository(db)
    assets = await repo.get_multi(limit=10000)
    if status:
        assets = [a for a in assets if a.status == status]
        
    filepath = ReportService.generate_pdf_report(assets)
    return FileResponse(path=filepath, filename="assets_report.pdf", media_type="application/pdf")
