import qrcode
import os
from app.core.config import settings

def generate_qr_code(qr_code_id: str) -> str:
    """
    Generate a QR code image for a given asset's qr_code_id.
    Returns the path to the saved image.
    """
    # The URL that the QR code will point to when scanned
    # In a real application, this should point to a frontend page that displays asset details
    url = f"https://yourdomain.com/assets/scan/{qr_code_id}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save the QR code image
    directory = "qrcodes"
    os.makedirs(directory, exist_ok=True)
    
    file_name = f"{qr_code_id}.png"
    file_path = os.path.join(directory, file_name)
    img.save(file_path)
    
    return f"/qrcodes/{file_name}"
