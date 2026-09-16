"""
Category Repository Interface
Repository port for category persistence
"""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List
from app.domain.entities.category import Category


class CategoryRepository(ABC):
    """
    Category repository interface
    Defines the contract for category persistence operations
    """

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Category]:
        """Get category by ID"""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Category]:
        """Get category by name"""
        pass

    @abstractmethod
    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
        parent_id: Optional[UUID] = None,
        search: Optional[str] = None
    ) -> List[Category]:
        """List categories with filtering and pagination"""
        pass

    @abstractmethod
    async def count(
        self,
        parent_id: Optional[UUID] = None,
        search: Optional[str] = None
    ) -> int:
        """Count categories with filtering"""
        pass

    @abstractmethod
    async def add(self, category: Category) -> Category:
        """Add new category"""
        pass

    @abstractmethod
    async def update(self, category: Category) -> Category:
        """Update existing category"""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Delete category by ID"""
        pass

    @abstractmethod
    async def get_children(self, parent_id: UUID) -> List[Category]:
        """Get child categories"""
        pass

    @abstractmethod
    async def get_assets_count(self, category_id: UUID) -> int:
        """Get count of assets in category"""
        pass