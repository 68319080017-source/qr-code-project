"""
Asset Entity
Core entity for asset management
"""

from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Dict, Any
from app.domain.value_objects.qr_code import QRCode
from app.domain.value_objects.asset_status import AssetStatus


@dataclass
class Asset:
    """
    Asset entity representing a physical or digital asset
    """
    id: UUID = field(default_factory=uuid4)
    code: str = field(default_factory=lambda: f"QR-{uuid4().hex[:8].upper()}")
    name: str = field(default="")
    description: Optional[str] = field(default=None)
    category_id: Optional[UUID] = field(default=None)
    location: Optional[str] = field(default=None)
    status: AssetStatus = field(default=AssetStatus.AVAILABLE)
    assigned_to: Optional[UUID] = field(default=None)
    created_by: Optional[UUID] = field(default=None)
    updated_by: Optional[UUID] = field(default=None)
    qr_code: Optional[bytes] = field(default=None)
    qr_code_url: Optional[str] = field(default=None)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    decommissioned_at: Optional[datetime] = field(default=None)

    def assign_to(self, user_id: UUID) -> None:
        """Assign asset to a user"""
        self.assigned_to = user_id
        self.status = AssetStatus.ASSIGNED
        self.updated_at = datetime.utcnow()

    def release(self) -> None:
        """Release asset assignment"""
        self.assigned_to = None
        self.status = AssetStatus.AVAILABLE
        self.updated_at = datetime.utcnow()

    def decommission(self) -> None:
        """Decommission asset"""
        self.status = AssetStatus.DECOMMISSIONED
        self.decommissioned_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def update_location(self, location: str) -> None:
        """Update asset location"""
        self.location = location
        self.updated_at = datetime.utcnow()

    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """Update asset metadata"""
        self.metadata.update(metadata)
        self.updated_at = datetime.utcnow()

    def generate_qr_code(self, qr_generator) -> None:
        """Generate QR code for asset"""
        self.qr_code = qr_generator.generate(self.code)
        self.qr_code_url = f"/api/v1/assets/{self.id}/qr"
        self.updated_at = datetime.utcnow()