"""
Authentication schemas for request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ============ Request Schemas ============

class UserRegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    name: str = Field(..., min_length=2, max_length=100)
    locale: str = Field(default="sk", pattern="^(sk|en)$")


class UserLoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class PasswordChangeRequest(BaseModel):
    """Password change request."""
    old_password: str
    new_password: str = Field(..., min_length=8)


class SessionRevokeRequest(BaseModel):
    """Session revocation request."""
    session_id: int
    reason: Optional[str] = "admin_revoked"


# ============ Response Schemas ============

class UserResponse(BaseModel):
    """User information response."""
    id: int
    email: str
    name: str
    role: str
    locale: str
    is_active: bool
    email_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    """Session information response."""
    id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    last_activity_at: datetime
    is_current: bool = False

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Login response with session token."""
    token: str
    user: UserResponse
    expires_at: datetime


class AuthStatusResponse(BaseModel):
    """Authentication status response."""
    authenticated: bool
    user: Optional[UserResponse] = None


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    success: bool = True


class SessionListResponse(BaseModel):
    """List of user sessions."""
    sessions: List[SessionResponse]
    total: int
