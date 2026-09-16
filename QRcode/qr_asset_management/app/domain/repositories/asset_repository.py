"""
Asset Repository Interface
Repository port for asset persistence
"""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List
from app.domain.entities.asset import Asset
from app.domain.value_objects.asset_status import AssetStatus


class AssetRepository(ABC):
    """
    Asset repository interface
    Defines the contract for asset persistence operations
    """

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Asset]:
        """Get asset by ID"""
        pass

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[Asset]:
        """Get asset by QR code"""
        pass

    @abstractmethod
    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
        status: Optional[AssetStatus] = None,
        category_id: Optional[UUID] = None,
        assigned_to: Optional[UUID] = None,
        search: Optional[str] = None
    ) -> List[Asset]:
        """List assets with filtering and pagination"""
        pass

    @abstractmethod
    async def count(
        self,
        status: Optional[AssetStatus] = None,
        category_id: Optional[UUID] = None,
        assigned_to: Optional[UUID] = None,
        search: Optional[str] = None
    ) -> int:
        """Count assets with filtering"""
        pass

    @abstractmethod
    async def add(self, asset: Asset) -> Asset:
        """Add new asset"""
        pass

    @abstractmethod
    async def update(self, asset: Asset) -> Asset:
        """Update existing asset"""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Delete asset by ID"""
        pass

    @abstractmethod
    async def assign_to(self, asset_id: UUID, user_id: UUID) -> Optional[Asset]:
        """Assign asset to user"""
        pass

    @abstractmethod
    async def release(self, asset_id: UUID) -> Optional[Asset]:
        """Release asset assignment"""
        pass

    @abstractmethod
    async def decommission(self, asset_id: UUID) -> Optional[Asset]:
        """Decommission asset"""
        pass

    @abstractmethod
    async def generate_qr_code(self, asset_id: UUID) -> Optional[bytes]:
        """Generate QR code for asset"""
        pass