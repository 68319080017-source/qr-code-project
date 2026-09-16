"""
Value Objects Package
Immutable objects that define entity characteristics
"""

from app.domain.value_objects.qr_code import QRCode
from app.domain.value_objects.asset_status import AssetStatus
from app.domain.value_objects.location import Location
from app.domain.value_objects.permission import Permission

__all__ = [
    "QRCode",
    "AssetStatus",
    "Location",
    "Permission",
]