"""
Role Entity
Core entity for RBAC role management
"""

from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List


@dataclass
class Role:
    """
    Role entity for Role-Based Access Control
    """
    id: UUID = field(default_factory=uuid4)
    name: str = field(default="")
    description: Optional[str] = field(default=None)
    permissions: List[str] = field(default_factory=list)
    is_system_role: bool = field(default=False)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def update_name(self, name: str) -> None:
        """Update role name"""
        self.name = name
        self.updated_at = datetime.utcnow()

    def update_description(self, description: Optional[str]) -> None:
        """Update role description"""
        self.description = description
        self.updated_at = datetime.utcnow()

    def add_permission(self, permission: str) -> None:
        """Add permission to role"""
        if permission not in self.permissions:
            self.permissions.append(permission)
            self.updated_at = datetime.utcnow()

    def remove_permission(self, permission: str) -> None:
        """Remove permission from role"""
        if permission in self.permissions:
            self.permissions.remove(permission)
            self.updated_at = datetime.utcnow()

    def has_permission(self, permission: str) -> bool:
        """Check if role has specific permission"""
        return permission in self.permissions

    def sync_permissions(self, permissions: List[str]) -> None:
        """Sync role permissions"""
        self.permissions = permissions
        self.updated_at = datetime.utcnow()


@dataclass
class Permission:
    """
    Permission entity for granular access control
    """
    id: str = field(default_factory=lambda: f"perm_{uuid4().hex[:8]}")
    resource: str = field(default="")
    action: str = field(default="")
    description: Optional[str] = field(default=None)

    @property
    def value(self) -> str:
        """Get permission value in format resource:action"""
        return f"{self.resource}:{self.action}"

    def matches(self, resource: str, action: str) -> bool:
        """Check if permission matches resource and action"""
        return self.resource == resource and self.action == action