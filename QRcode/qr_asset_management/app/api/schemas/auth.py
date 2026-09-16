"""
Authentication Schemas
Request and response models for authentication endpoints
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class Token(BaseModel):
    """JWT token response model"""
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


class TokenPayload(BaseModel):
    """JWT token payload model"""
    sub: str = Field(..., description="Subject (user ID)")
    exp: int = Field(..., description="Expiration timestamp")
    type: str = Field(..., description="Token type (access/refresh)")
    roles: Optional[list[str]] = Field(default=None, description="User roles")
    permissions: Optional[list[str]] = Field(default=None, description="User permissions")


class TokenRefresh(BaseModel):
    """Token refresh request model"""
    refresh_token: str = Field(..., description="Refresh token")


class UserLogin(BaseModel):
    """User login request model"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")


class UserResponse(BaseModel):
    """User response model"""
    id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    first_name: Optional[str] = Field(default=None, description="User first name")
    last_name: Optional[str] = Field(default=None, description="User last name")
    is_active: bool = Field(default=True, description="User active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """User creation request model"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")
    first_name: Optional[str] = Field(default=None, description="User first name")
    last_name: Optional[str] = Field(default=None, description="User last name")
    role_id: Optional[str] = Field(default=None, description="Assigned role ID")


class UserUpdate(BaseModel):
    """User update request model"""
    first_name: Optional[str] = Field(default=None, description="User first name")
    last_name: Optional[str] = Field(default=None, description="User last name")
    email: Optional[EmailStr] = Field(default=None, description="User email")
    is_active: Optional[bool] = Field(default=None, description="User active status")