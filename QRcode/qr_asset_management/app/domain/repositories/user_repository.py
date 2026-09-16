"""
User Repository Interface
Repository port for user persistence
"""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List
from app.domain.entities.user import User, UserStatus


class UserRepository(ABC):
    """
    User repository interface
    Defines the contract for user persistence operations
    """

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[User]:
        """Get user by ID"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass

    @abstractmethod
    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[User]:
        """List users with filtering and pagination"""
        pass

    @abstractmethod
    async def count(
        self,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> int:
        """Count users with filtering"""
        pass

    @abstractmethod
    async def add(self, user: User) -> User:
        """Add new user"""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update existing user"""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Delete user by ID"""
        pass

    @abstractmethod
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        pass

    @abstractmethod
    async def update_last_login(self, id: UUID) -> None:
        """Update user's last login timestamp"""
        pass

    @abstractmethod
    async def assign_role(self, user_id: UUID, role_id: UUID) -> bool:
        """Assign role to user"""
        pass

    @abstractmethod
    async def remove_role(self, user_id: UUID, role_id: UUID) -> bool:
        """Remove role from user"""
        pass

    @abstractmethod
    async def get_roles(self, user_id: UUID) -> List[UUID]:
        """Get user's role IDs"""
        pass