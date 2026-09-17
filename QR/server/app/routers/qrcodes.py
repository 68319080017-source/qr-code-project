import io
import qrcode
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()

# Domain ของ Render สำหรับสร้าง QR Code สแกนได้ 24 ชม.
RENDER_URL = "https://qr-code-project-8nj6.onrender.com"

@router.get("/generate/{asset_code}")
def generate_qr(asset_code: str, request: Request, db: Session = Depends(get_db)):
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