"""
User Entity
Core entity for user management
"""

from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List
from enum import Enum


class UserStatus(Enum):
    """User status enumeration"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"


@dataclass
class User:
    """
    User entity representing a system user
    """
    id: UUID = field(default_factory=uuid4)
    email: str = field(default="")
    password_hash: str = field(default="")
    first_name: Optional[str] = field(default=None)
    last_name: Optional[str] = field(default=None)
    is_active: bool = field(default=True)
    is_verified: bool = field(default=False)
    status: UserStatus = field(default=UserStatus.ACTIVE)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = field(default=None)
    role_ids: List[UUID] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.email

    def update_password(self, password_hash: str) -> None:
        """Update user password hash"""
        self.password_hash = password_hash
        self.updated_at = datetime.utcnow()

    def update_profile(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None
    ) -> None:
        """Update user profile"""
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        if email is not None:
            self.email = email
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate user account"""
        self.is_active = True
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate user account"""
        self.is_active = False
        self.status = UserStatus.INACTIVE
        self.updated_at = datetime.utcnow()

    def update_last_login(self) -> None:
        """Update last login timestamp"""
        self.last_login_at = datetime.utcnow()