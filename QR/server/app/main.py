import os
from datetime import datetime
import zoneinfo
from fastapi import FastAPI, Request, Form, Response, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app import models

# Import Routers
from app.routers import assets, maintenance, qrcodes, reports, users

app = FastAPI(title="Asset Management System")

# ตั้งค่า Timezone เวลาประเทศไทย (UTC+7)
THAI_TZ = zoneinfo.ZoneInfo("Asia/Bangkok")

# =========================================================
# CONFIG & AUTH SETTINGS
# =========================================================
ADMIN_USER = "admin"
ADMIN_PASS = "2026"

SESSION_COOKIE_KEY = "admin_session"
USER_COOKIE_KEY = "logged_user"

# ความจำแรมกลางสำหรับนับแอดมินที่ออนไลน์
ACTIVE_ADMIN_SESSIONS = {}

# Mount Static & Uploads
app.mount("/static", StaticFiles(directory="app/static"), name="static")

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="app/templates")

def is_authenticated(request: Request) -> bool:
    session = request.cookies.get(SESSION_COOKIE_KEY)
    return session == "valid_admin_token_2026"

def require_admin(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return None

# =========================================================
# REAL-TIME ADMIN TRACKER API (จับ IP แท้ + อุปกรณ์ + เวลาไทย)
# =========================================================
@app.post("/api/v1/active-admins")
async def track_active_admin(request: Request):
    data = await request.json()
    device_id = data.get("device_id")
    
    if not device_id:
        return JSONResponse({"status": "error"}, status_code=400)
    
    # 1. ดักจับ IP แท้จริงผ่าน Header บน Cloud/Render
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "Unknown IP"
        
    user_agent = request.headers.get("user-agent", "")
    
    # 2. จำแนกประเภทอุปกรณ์แบบละเอียด
    if "iPhone" in user_agent or "Android" in user_agent:
        device_name = "Mobile (โทรศัพท์มือถือ)"
    elif "iPad" in user_agent or "Tablet" in user_agent:
        device_name = "Tablet (แท็บเล็ต)"
    elif "Macintosh" in user_agent or "Mac OS" in user_agent:
        device_name = "MacBook / Mac"
    elif "Windows" in user_agent:
        device_name = "PC / Laptop (Windows)"
    else:
        device_name = "Desktop / Web Browser"
    
    # 3. เวลาไทยปัจจุบัน
    now_thai = datetime.now(THAI_TZ).strftime("%H:%M:%S")

    # บันทึกข้อมูลเข้าเซิร์ฟเวอร์
    ACTIVE_ADMIN_SESSIONS[device_id] = {
        "ip": client_ip,
        "device": device_name,
        "last_seen": now_thai
    }
    
    # แปลงส่งกลับให้หน้าบ้าน
    admin_list = []
    for idx, (d_id, d_info) in enumerate(ACTIVE_ADMIN_SESSIONS.items(), start=1):
        admin_list.append({
            "code": f"admin{idx:02d}",
            "ip": d_info["ip"],
            "device": d_info["device"],
            "last_seen": d_info["last_seen"],
            "is_me": (d_id == device_id)
        })
        
    return {"active_count": len(admin_list), "admins": admin_list}

# =========================================================
# AUTHENTICATION ROUTES
# =========================================================
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login")
def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and password == ADMIN_PASS:
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key=SESSION_COOKIE_KEY, value="valid_admin_token_2026", httponly=True, max_age=86400)
        response.set_cookie(key=USER_COOKIE_KEY, value="admin", httponly=False, max_age=86400)
        return response
    return templates.TemplateResponse(request=request, name="login.html", context={"error": "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง!"})

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(SESSION_COOKIE_KEY)
    response.delete_cookie(USER_COOKIE_KEY)
    return response

# =========================================================
# WEB PAGES ROUTES
# =========================================================
@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def view_dashboard(request: Request):
    redirect = require_admin(request)
    if redirect: return redirect
    return templates.TemplateResponse(request=request, name="dashboard.html")

@app.get("/assets", response_class=HTMLResponse)
def view_assets_page(request: Request):
    redirect = require_admin(request)
    if redirect: return redirect
    return templates.TemplateResponse(request=request, name="assets.html")

@app.get("/qrcodes", response_class=HTMLResponse)
def view_qrcodes_page(request: Request):
    redirect = require_admin(request)
    if redirect: return redirect
    return templates.TemplateResponse(request=request, name="qrcodes.html")

@app.get("/maintenance", response_class=HTMLResponse)
def view_maintenance_page(request: Request):
    redirect = require_admin(request)
    if redirect: return redirect
    return templates.TemplateResponse(request=request, name="maintenance.html")

@app.get("/reports", response_class=HTMLResponse)
def view_reports_page(request: Request):
    redirect = require_admin(request)
    if redirect: return redirect
    return templates.TemplateResponse(request=request, name="reports.html")

@app.get("/users", response_class=HTMLResponse)
def view_users_page(request: Request):
    redirect = require_admin(request)
    if redirect: return redirect
    return templates.TemplateResponse(request=request, name="users.html")

@app.get("/scan/{asset_code}", response_class=HTMLResponse)
def view_public_scan(asset_code: str, request: Request, db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter(models.Asset.asset_code == asset_code).first()
    return templates.TemplateResponse(request=request, name="user_scan.html", context={"asset": asset})

app.include_router(assets.router, prefix="/api/v1/assets", tags=["Assets API"])
app.include_router(maintenance.router, prefix="/api/v1/maintenance", tags=["Maintenance API"])
app.include_router(qrcodes.router, prefix="/api/v1/qrcodes", tags=["QR Codes API"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports API"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users API"])