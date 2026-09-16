from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import qrcode
import io
from app.database import get_db

router = APIRouter()

@router.get("/generate/{asset_code}")
def generate_qr(asset_code: str, request: Request, db: Session = Depends(get_db)):
    # ดึง URL จาก Render อัตโนมัติ (ไม่ใช้ ngrok แล้ว)
    base_url = str(request.base_url).rstrip('/')
    redirect_url = f"{base_url}/scan/{asset_code}"
    
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

    return StreamingResponse(
        img_byte_arr, 
        media_type="image/png",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )