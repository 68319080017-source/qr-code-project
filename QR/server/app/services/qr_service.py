import qrcode
import os
from PIL import Image

class QRService:
    @staticmethod
    def generate_qr_code(asset_code: str, base_url: str = "http://localhost:8000") -> str:
        """
        Generates a QR code for the given asset code.
        Saves it to the qrcodes directory and returns the path.
        """
        # Ensure directory exists
        qr_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "qrcodes")
        os.makedirs(qr_dir, exist_ok=True)
        
        url = f"{base_url}/asset/scan/{asset_code}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        filename = f"{asset_code}.png"
        filepath = os.path.join(qr_dir, filename)
        img.save(filepath)
        
        return f"/qrcodes/{filename}"
