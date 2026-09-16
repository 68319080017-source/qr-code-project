from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import qrcode
import io
from app.database import get_db

router = APIRouter()

# 🔴 ลิงก์ ngrok ที่ใช้งานได้ปัจจุบัน
NGROK_BASE_URL = "https://wimp-democrat-swampland.ngrok-free.dev"

@router.get("/generate/{asset_code}")
def generate_qr(asset_code: str, request: Request, db: Session = Depends(get_db)):
    # บังคับใช้ ngrok URL เท่านั้น ห้ามอ้างอิง localhost
    redirect_url = f"{NGROK_BASE_URL}/scan/{asset_code}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(redirect_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return StreamingResponse(img_byte_arr, media_type="image/png")