"""
Category Entity
Core entity for asset categorization
"""

from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List


@dataclass
class Category:
    """
    Category entity for organizing assets
    """
    id: UUID = field(default_factory=uuid4)
    name: str = field(default="")
    description: Optional[str] = field(default=None)
    parent_id: Optional[UUID] = field(default=None)
    icon: Optional[str] = field(default=None)
    color: Optional[str] = field(default=None)
    asset_count: int = field(default=0)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def update_name(self, name: str) -> None:
        """Update category name"""
        self.name = name
        self.updated_at = datetime.utcnow()

    def update_description(self, description: Optional[str]) -> None:
        """Update category description"""
        self.description = description
        self.updated_at = datetime.utcnow()

    def set_icon(self, icon: Optional[str]) -> None:
        """Set category icon"""
        self.icon = icon
        self.updated_at = datetime.utcnow()

    def set_color(self, color: Optional[str]) -> None:
        """Set category color"""
        self.color = color
        self.updated_at = datetime.utcnow()

    def increment_asset_count(self) -> None:
        """Increment asset count"""
        self.asset_count += 1

    def decrement_asset_count(self) -> None:
        """Decrement asset count"""
        self.asset_count = max(0, self.asset_count - 1)