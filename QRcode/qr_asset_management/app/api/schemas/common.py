"""
Common Schemas
Shared request and response models
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, TypeVar, Generic
from uuid import UUID


T = TypeVar('T')


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model"""
    data: List[T] = Field(..., description="Response data")
    meta: PaginationMeta = Field(..., description="Pagination metadata")


class ErrorDetail(BaseModel):
    """Error detail model"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(default=None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: ErrorDetail = Field(..., description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class SuccessResponse(BaseModel, Generic[T]):
    """Success response model"""
    data: T = Field(..., description="Response data")
    message: Optional[str] = Field(default="Success", description="Response message")


class HealthCheck(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")


class AuditLog(BaseModel):
    """Audit log response model"""
    id: UUID = Field(..., description="Log ID")
    user_id: Optional[UUID] = Field(default=None, description="User ID")
    asset_id: Optional[UUID] = Field(default=None, description="Asset ID")
    action: str = Field(..., description="Action performed")
    details: Optional[dict] = Field(default=None, description="Action details")
    timestamp: datetime = Field(..., description="Action timestamp")
    ip_address: Optional[str] = Field(default=None, description="Client IP address")

    class Config:
        from_attributes = True