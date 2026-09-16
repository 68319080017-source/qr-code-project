from app.database.connection import engine, Base, get_db
from app.models.asset import Asset
from app.models.maintenance import Maintenance
from app.models.user import User
from sqlalchemy.orm import Session
from sqlalchemy import select

# รายการ Asset ตั้งต้นที่จะยัดลง DB (เพิ่มรายการตรงนี้ได้เรื่อยๆ)
INITIAL_ASSETS = [
    {"asset_code": "001", "name": "คอมพิวเตอร์ประมวลผล", "status": "ใช้งานได้ปกติ"},
    {"asset_code": "002", "name": "เครื่องพิมพ์ HP LaserJet", "status": "ใช้งานได้ปกติ"},
    {"asset_code": "003", "name": "จอมอนิเตอร์ Dell 24 นิ้ว", "status": "ใช้งานได้ปกติ"},
    {"asset_code": "004", "name": "โปรเจกเตอร์ Epson", "status": "ใช้งานได้ปกติ"},
]

def init_official_db():
    print("🔄 กำลังเตรียมโครงสร้างฐานข้อมูล...")
    
    # 1. สร้าง Table ทั้งหมดจาก Models (แบบ Sync Engine)
    Base.metadata.create_all(bind=engine)
    print("✅ สร้าง Schema ตารางข้อมูลเรียบร้อยแล้ว")

    # 2. เปิด Session เพื่อเพิ่มข้อมูล Assets
    with Session(engine) as session:
        for item in INITIAL_ASSETS:
            stmt = select(Asset).where(Asset.asset_code == item["asset_code"])
            existing_asset = session.execute(stmt).scalar_one_or_none()

            if not existing_asset:
                new_asset = Asset(
                    asset_code=item["asset_code"],
                    name=item["name"],
                    status=item["status"]
                )
                session.add(new_asset)
                print(f"  └─ เพิ่ม Asset: {item['asset_code']} - {item['name']}")

        session.commit()

    print("🚀 ระบบฐานข้อมูลพร้อมรองรับการใช้งานจริงเรียบร้อย!")

if __name__ == "__main__":
    init_official_db()