# QR Code Asset Management System

ระบบจัดการครุภัณฑ์ผ่าน QR Code (QR Asset Management System) เป็นแอปพลิเคชันสำหรับบริหารจัดการครุภัณฑ์ภายในองค์กร พร้อมระบบสแกน QR Code สำหรับเข้าถึงข้อมูลและแจ้งซ่อมผ่านสมาร์ทโฟน

## 🌟 ฟีเจอร์หลัก (Key Features)

- 🔐 **ระบบ Authentication & RBAC**: รองรับผู้ใช้งานหลายระดับ (Super Admin, Admin, พัสดุ, ผู้ใช้งานทั่วไป)
- 📦 **การจัดการครุภัณฑ์ (Asset Management)**: เพิ่ม, แก้ไข, ลบ และออก QR Code อัตโนมัติ
- 📱 **QR Scanner**: หน้าจอสำหรับมือถือเพื่อสแกน QR Code พร้อมเข้าสู่หน้าข้อมูลครุภัณฑ์ทันที
- 📝 **ระบบแจ้งซ่อม (Maintenance Log)**: รายงานอาการชำรุด พร้อมแนบรูปภาพก่อนซ่อม-หลังซ่อม
- 🔍 **ระบบตรวจสอบ (Audit Log)**: การเช็คสต๊อกครุภัณฑ์ประจำปี
- 📊 **Dashboard**: สรุปจำนวนครุภัณฑ์แยกตามสถานะ
- 📤 **Export**: รองรับการนำออกข้อมูลเป็น Excel และ PDF

## 💻 เทคโนโลยีที่ใช้ (Tech Stack)

- **Backend**: FastAPI (Python 3.14)
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **ORM**: SQLAlchemy + Alembic (Migrations)
- **Frontend**: HTML5, Vanilla JS, Bootstrap 5, FontAwesome 6 (Jinja2 Templates)
- **Containerization**: Docker & Docker Compose

## 🚀 การติดตั้งและใช้งาน (Installation)

### วิธีที่ 1: รันด้วย Docker (แนะนำสำหรับ Production)

ระบบมี Docker Compose เตรียมไว้ให้พร้อมใช้งาน (รวม PostgreSQL และ Backend)

1. เปิด Terminal / PowerShell
2. รันคำสั่งต่อไปนี้:
   ```bash
   docker-compose up -d --build
   ```
3. เข้าใช้งานที่เบราว์เซอร์: `http://localhost:8000`

### วิธีที่ 2: รันแบบ Development (Local)

1. สร้าง Virtual Environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. ติดตั้ง Dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. รัน Server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
4. เข้าใช้งานที่: `http://localhost:8000`

## 🔑 บัญชีเริ่มต้น (Default Accounts)

- **Super Admin**: `admin@qrasset.local`
- **Password**: `admin1234`

## 📂 โครงสร้างโปรเจกต์ (Project Structure)

```
app/
├── core/         # การตั้งค่า Security, Config ฯลฯ
├── database/     # การเชื่อมต่อฐานข้อมูล (Session, Base)
├── models/       # SQLAlchemy Models (โครงสร้างตารางใน DB)
├── schemas/      # Pydantic Schemas (สำหรับ Validate ข้อมูลเข้า/ออก)
├── routers/      # API Routes (แบ่งตาม Features เช่น assets, users)
├── services/     # Business logic เช่น การสร้าง QR, ออก Excel/PDF
├── static/       # ไฟล์ JS, CSS, รูปภาพ
└── templates/    # ไฟล์ HTML (Jinja2)
```

## 🧪 การทดสอบ (Testing)

ระบบมีการเตรียม `pytest` เอาไว้แล้ว สามารถรันชุดทดสอบได้ด้วยคำสั่ง:
```bash
pytest tests/
```
