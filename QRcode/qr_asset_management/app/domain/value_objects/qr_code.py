"""
QR Code Value Object
Immutable value object for QR code representation
"""

from dataclasses import dataclass
from typing import Optional
import qrcode
from io import BytesIO


@dataclass(frozen=True)
class QRCode:
    """
    QR code value object
    Immutable representation of a QR code
    """
    data: str
    size: int = 300
    border: int = 4
    format: str = "png"
    error_correction: str = "M"

    def generate(self) -> bytes:
        """Generate QR code as bytes"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{self.error_correction}"),
            box_size=10,
            border=self.border,
        )
        qr.add_data(self.data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        if self.format.lower() == "png":
            img.save(buffer, format="PNG")
        elif self.format.lower() == "jpeg":
            img.save(buffer, format="JPEG")
        else:
            img.save(buffer, format="PNG")
        
        return buffer.getvalue()

    def generate_with_options(self, **options) -> bytes:
        """Generate QR code with custom options"""
        qr = qrcode.QRCode(
            version=options.get("version", 1),
            error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{options.get('error_correction', 'M')}"),
            box_size=options.get("box_size", 10),
            border=options.get("border", self.border),
        )
        qr.add_data(self.data)
        qr.make(fit=True)
        
        img = qr.make_image(
            fill_color=options.get("fill_color", "black"),
            back_color=options.get("back_color", "white")
        )
        
        buffer = BytesIO()
        img.save(buffer, format=options.get("format", self.format).upper())
        return buffer.getvalue()

    @classmethod
    def from_string(cls, data: str, **options) -> "QRCode":
        """Create QR code from string data"""
        return cls(
            data=data,
            size=options.get("size", 300),
            border=options.get("border", 4),
            format=options.get("format", "png"),
            error_correction=options.get("error_correction", "M"),
        )