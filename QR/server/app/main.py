import os
import requests
import zoneinfo
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, Request, Form, Depends, status, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

# Database Connections & Models Import
from app.database.connection import Base, engine, get_db
from app.models import asset, maintenance, requisition, user  # สั่ง Import ให้ SQLAlchemy รู้จัก Table ทั้งหมด

# Router Imports
from app.routers import assets, maintenance, qrcodes, reports, users, requisitions

# =========================================================
# INITIALIZATION & AUTO DB MIGRATION
# =========================================================
# 1. สร้างตารางพื้นฐานอัตโนมัติหากยังไม่มี
Base.metadata.create_all(bind=engine)

# 2. ฟังก์ชันตรวจสอบและเพิ่มคอลัมน์ที่ขาดไป (รองรับทั้ง SQLite และ PostgreSQL)
def run_db_migrations():
    columns_to_add = ["location", "serial_number", "building", "room"]
    for col in columns_to_add:
        try:
            with engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE assets ADD COLUMN {col} VARCHAR;"))
                conn.commit()
        except Exception:
            # ถ้ามีคอลัมน์นี้อยู่แล้ว หรือไวยากรณ์ซ้ำ จะข้ามไปโดยไม่ทำให้โปรแกรมล่ม
            pass

run_db_migrations()

app = FastAPI(
    title="Asset Management System",
    description="ระบบบริหารจัดการครุภัณฑ์ พร้อมระบบสแกน QR Code และ Audit Log Timeline",
    version="2.0.0"
)

# ตั้งค่า Timezone ประเทศไทย (UTC+7)
THAI_TZ = zoneinfo.ZoneInfo("Asia/Bangkok")

# LINE Messaging API Config (ใช้แทน LINE Notify ที่ยุติบริการ)
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "YOUR_LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_OR_GROUP_ID = os.getenv("LINE_USER_OR_GROUP_ID", "YOUR_LINE_USER_OR_GROUP_ID")

# Authentication Credentials
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "2026")

SESSION_COOKIE_KEY = "admin_session"
USER_COOKIE_KEY = "logged_user"

# หน่วยความจำชั่วคราวสำหรับนับ Admin ที่ออนไลน์แบบ Real-time
ACTIVE_ADMIN_SESSIONS = {}

# Mount Static Files & Uploads Directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="app/templates")


# =========================================================
# HELPER & AUTH FUNCTIONS
# =========================================================
def is_authenticated(request: Request) -> bool:
    """ตรวจสอบ Session จาก Cookie"""
    session = request.cookies.get(SESSION_COOKIE_KEY)
    return session == "valid_admin_token_2026"

def require_admin(request: Request):
    """Middleware ตรวจสอบสิทธิ์ Admin ก่อนเข้าถึงหน้า Dashboard/Management"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return None

def send_line_push_message(text_message: str):
    """ฟังก์ชันส่งข้อความแจ้งเตือนผ่าน LINE Messaging API แบบ Background Task"""
    if not LINE_CHANNEL_ACCESS_TOKEN or LINE_CHANNEL_ACCESS_TOKEN.startswith("YOUR_"):
        print("[LINE API Warning] ยังไม่ได้กำหนด LINE_CHANNEL_ACCESS_TOKEN")
        return

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "to": LINE_USER_OR_GROUP_ID,
        "messages": [
            {
                "type": "text",
                "text": text_message
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        if response.status_code != 200:
            print(f"[LINE API Error] {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[LINE API Exception] {str(e)}")


# =========================================================
# PYDANTIC SCHEMAS FOR SYSTEM APIs
# =========================================================
class LineNotifyPayload(BaseModel):
    message: str

class AuditLogCreate(BaseModel):
    asset_id: str
    action: str
    action_by: str
    details: Optional[str] = None


# =========================================================
# REAL-TIME ADMIN TRACKER API
# =========================================================
@app.post("/api/v1/active-admins")
async def track_active_admin(request: Request):
    """API ดักจับและระบุตัวตน อุปกรณ์/IP ของ Admin ที่ใช้งานอยู่ในขณะนั้น"""
    try:
        data = await request.json()
    except Exception:
        data = {}

    device_id = data.get("device_id")
    if not device_id:
        return JSONResponse({"status": "error", "message": "Missing device_id"}, status_code=400)

    # 1. ดักจับ IP ที่แท้จริง (รองรับกรณีผ่าน Reverse Proxy / Nginx)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "Unknown IP"

    user_agent = request.headers.get("user-agent", "")

    # 2. จำแนกประเภทอุปกรณ์ของผู้ใช้งาน
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

    # 3. สแตมป์เวลาปัจจุบันของประเทศไทย
    now_thai = datetime.now(THAI_TZ).strftime("%H:%M:%S")

    # บันทึกข้อมูลลงใน Memory
    ACTIVE_ADMIN_SESSIONS[device_id] = {
        "ip": client_ip,
        "device": device_name,
        "last_seen": now_thai
    }

    # แปลงโครงสร้างข้อมูลส่งกลับไปให้หน้า Frontend
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
# AUDIT LOG & LINE NOTIFY APIS
# =========================================================
@app.post("/api/v1/notify/line", tags=["Notifications API"])
async def send_line_notification(payload: LineNotifyPayload, background_tasks: BackgroundTasks):
    """API สำหรับส่งข้อความแจ้งเตือนเข้า LINE กลุ่มช่าง/Admin"""
    background_tasks.add_task(send_line_push_message, payload.message)
    return {"status": "success", "message": "คำขอส่งการแจ้งเตือนถูกดำเนินการแล้ว"}


@app.post("/api/v1/audit-log/add", tags=["Audit Log API"])
async def create_audit_log(log: AuditLogCreate):
    """API บันทึกประวัติกิจกรรมของครุภัณฑ์ (Audit Log)"""
    timestamp = datetime.now(THAI_TZ).strftime("%d %b %Y - %H:%M น.")
    log_entry = {
        "asset_id": log.asset_id,
        "action": log.action,
        "action_by": log.action_by,
        "details": log.details,
        "timestamp": timestamp
    }
    return {"status": "success", "data": log_entry}


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
    return templates.TemplateResponse(
        request=request, 
        name="login.html", 
        context={"error": "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง!"}
    )

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(SESSION_COOKIE_KEY)
    response.delete_cookie(USER_COOKIE_KEY)
    return response


# =========================================================
# WEB PAGES ROUTES (ADMIN DASHBOARD & PANELS)
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

@app.get("/requisitions", response_class=HTMLResponse)
def view_requisitions_page(request: Request):
    redirect = require_admin(request)
    if redirect: return redirect
    return templates.TemplateResponse(request=request, name="requisitions.html")

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
    """หน้า Public สำหรับแสดงข้อมูลครุภัณฑ์ เมื่อผู้ใช้ทั่วไปสแกนผ่าน QR Code"""
    asset_obj = db.query(asset.Asset).filter(asset.Asset.asset_code == asset_code).first()
    return templates.TemplateResponse(request=request, name="user_scan.html", context={"asset": asset_obj})


# =========================================================
# INCLUDE ROUTERS
# =========================================================
app.include_router(assets.router, prefix="/api/v1/assets", tags=["Assets API"])
app.include_router(maintenance.router, prefix="/api/v1/maintenance", tags=["Maintenance API"])
app.include_router(requisitions.router, prefix="/api/v1/requisitions", tags=["Requisitions API"])
app.include_router(qrcodes.router, prefix="/api/v1/qrcodes", tags=["QR Codes API"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports API"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users API"])