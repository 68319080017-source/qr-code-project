import io
import qrcode
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()

# 🌐 ใส่ URL บน Render ของคุณที่เปิดได้ 24 ชม. ตรงนี้ (เช่น https://xxx-nj6.onrender.com)
RENDER_URL = "https://your-app-name.onrender.com" 

@router.get("/generate/{asset_code}")
def generate_qr(asset_code: str, request: Request, db: Session = Depends(get_db)):
    # บังคับฝัง URL ของ Render ลงใน QR Code ทุกใบตลอดเวลา
    redirect_url = f"{RENDER_URL.rstrip('/')}/scan/{asset_code}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(redirect_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return StreamingResponse(
        img_byte_arr, 
        media_type="image/png",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )