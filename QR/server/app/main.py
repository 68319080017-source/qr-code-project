import os
from fastapi import FastAPI, Request, Form, Response, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app import models

# Import Routers
from app.routers import assets, maintenance, qrcodes, reports, users

app = FastAPI(title="Asset Management System")

# =========================================================
# CONFIG & AUTH SETTINGS
# =========================================================
ADMIN_USER = "admin"
ADMIN_PASS = "2026"
SESSION_COOKIE_KEY = "admin_session"

# Mount Static & Uploads
app.mount("/static", StaticFiles(directory="app/static"), name="static")

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Config Jinja2 Templates
templates = Jinja2Templates(directory="app/templates")


# Helper Check Auth Session
def is_authenticated(request: Request) -> bool:
    session = request.cookies.get(SESSION_COOKIE_KEY)
    return session == "valid_admin_token_2026"


# Helper Redirect Guard for Unauthenticated Access
def require_admin(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return None


# =========================================================
# AUTHENTICATION ROUTES (ระบบเข้า/ออกจากระบบ)
# =========================================================

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )

@app.post("/login")
def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and password == ADMIN_PASS:
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        response.set_cookie(
            key=SESSION_COOKIE_KEY, 
            value="valid_admin_token_2026", 
            httponly=True, 
            max_age=86400  # มีอายุใช้งาน 1 วัน
        )
        return response
    
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง!"}
    )

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(SESSION_COOKIE_KEY)
    return response


# =========================================================
# WEB PAGES ROUTES (หน้าเว็บสำหรับ Admin - Protected)
# =========================================================

# 1. หน้าแรก / Dashboard
@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def view_dashboard(request: Request):
    redirect = require_admin(request)
    if redirect: return redirect
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html"
    )

# 2. หน้า รายการครุภัณฑ์ทั้งหมด
@app.get("/assets", response_class=HTMLResponse)
def view_assets_page(request: Request):
    redirect = require_admin(request)
    if redirect: return redirect
    return templates.TemplateResponse(
        request=request,
        name="assets.html"
    )

# 3. หน้า พิมพ์ QR Code
@app.get("/qrcodes", response_class=HTMLResponse)
def view_qrcodes_page(request: Request):
    redirect = require_admin(request)
    if redirect: return redirect
    return templates.TemplateResponse(
        request=request,
        name="qrcodes.html"
    )

# 4. หน้า แจ้งซ่อม / บำรุง
@app.get("/maintenance", response_class=HTMLResponse)
def view_maintenance_page(request: Request):
    redirect = require_admin(request)
    if redirect: return redirect
    return templates.TemplateResponse(
        request=request,
        name="maintenance.html"
    )

# 5. หน้า ออกรายงาน / Report
@app.get("/reports", response_class=HTMLResponse)
def view_reports_page(request: Request):
    redirect = require_admin(request)
    if redirect: return redirect
    return templates.TemplateResponse(
        request=request,
        name="reports.html"
    )

# 6. หน้า สิทธิ์ผู้ใช้งาน
@app.get("/users", response_class=HTMLResponse)
def view_users_page(request: Request):
    redirect = require_admin(request)
    if redirect: return redirect
    return templates.TemplateResponse(
        request=request,
        name="users.html"
    )


# =========================================================
# PUBLIC SCAN ROUTE (หน้าสำหรับผู้ใช้ทั่วไปสแกน QR Code - Public)
# =========================================================
@app.get("/scan/{asset_code}", response_class=HTMLResponse)
def view_public_scan(asset_code: str, request: Request, db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter(models.Asset.asset_code == asset_code).first()
    
    return templates.TemplateResponse(
        request=request,
        name="user_scan.html",
        context={"asset": asset}
    )


# =========================================================
# INCLUDE API ROUTERS
# =========================================================
app.include_router(assets.router, prefix="/api/v1/assets", tags=["Assets API"])
app.include_router(maintenance.router, prefix="/api/v1/maintenance", tags=["Maintenance API"])
app.include_router(qrcodes.router, prefix="/api/v1/qrcodes", tags=["QR Codes API"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports API"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users API"])