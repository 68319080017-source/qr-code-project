"""
Audit Log Entity
Core entity for activity tracking
"""

from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class AuditAction(Enum):
    """Audit action types"""
    # User actions
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    USER_LOGIN = "USER_LOGIN"
    USER_LOGOUT = "USER_LOGOUT"
    
    # Asset actions
    ASSET_CREATED = "ASSET_CREATED"
    ASSET_UPDATED = "ASSET_UPDATED"
    ASSET_DELETED = "ASSET_DELETED"
    ASSET_ASSIGNED = "ASSET_ASSIGNED"
    ASSET_RELEASED = "ASSET_RELEASED"
    ASSET_DECOMMISSIONED = "ASSET_DECOMMISSIONED"
    
    # Category actions
    CATEGORY_CREATED = "CATEGORY_CREATED"
    CATEGORY_UPDATED = "CATEGORY_UPDATED"
    CATEGORY_DELETED = "CATEGORY_DELETED"
    
    # Role actions
    ROLE_CREATED = "ROLE_CREATED"
    ROLE_UPDATED = "ROLE_UPDATED"
    ROLE_DELETED = "ROLE_DELETED"
    PERMISSION_GRANTED = "PERMISSION_GRANTED"
    PERMISSION_REVOKED = "PERMISSION_REVOKED"


@dataclass
class AuditLog:
    """
    Audit log entity for tracking all system activities
    """
    id: UUID = field(default_factory=uuid4)
    user_id: Optional[UUID] = field(default=None)
    asset_id: Optional[UUID] = field(default=None)
    action: AuditAction = field(default=AuditAction.USER_LOGIN)
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = field(default=None)
    user_agent: Optional[str] = field(default=None)
    request_id: Optional[str] = field(default=None)

    @classmethod
    def create(
        cls,
        action: AuditAction,
        user_id: Optional[UUID] = None,
        asset_id: Optional[UUID] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> "AuditLog":
        """Factory method to create audit log entry"""
        return cls(
            user_id=user_id,
            asset_id=asset_id,
            action=action,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
        )