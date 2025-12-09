"""
Authentication schemas for API v1.
Prepared for Better Auth integration.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from .base import BaseSchema


# ==================== User Schemas ====================

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8)


class UserResponse(BaseSchema):
    """User response schema."""
    id: str
    email: EmailStr
    name: Optional[str] = None
    role: str = "user"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserListResponse(BaseModel):
    """List of users (admin only)."""
    items: list[UserResponse]
    total: int


# ==================== Auth Schemas ====================

class LoginRequest(BaseModel):
    """Login request."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str  # user id
    email: str
    role: str
    exp: datetime


class CurrentUserResponse(BaseModel):
    """Current authenticated user."""
    user: UserResponse
    permissions: list[str]


# ==================== Session Schemas ====================

class SessionInfo(BaseModel):
    """Session information."""
    id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


# ==================== API Key Schemas (alternative auth) ====================

class APIKeyCreate(BaseModel):
    """Create new API key."""
    name: str = Field(..., description="Name/description for the API key")
    expires_in_days: Optional[int] = Field(
        default=None,
        description="Expiration in days (None = never expires)"
    )


class APIKeyResponse(BaseModel):
    """API key response (key shown only once)."""
    id: str
    name: str
    key: str  # Only shown on creation
    created_at: datetime
    expires_at: Optional[datetime] = None


class APIKeyListItem(BaseModel):
    """API key list item (without actual key)."""
    id: str
    name: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None

