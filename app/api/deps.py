"""
Common dependencies for API endpoints.
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, get_db
from app.services.audit import AuditLogger
from app.services.storage import StorageService


# ==================== Database ====================

def get_database() -> Generator[Session, None, None]:
    """
    Database session dependency.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== Services ====================

def get_audit_logger() -> AuditLogger:
    """Get audit logger instance."""
    return AuditLogger()


def get_storage_service() -> StorageService:
    """Get storage service instance."""
    return StorageService()


# ==================== Auth (Placeholder for Better Auth) ====================

class CurrentUser:
    """
    Placeholder for authenticated user.
    Will be replaced with Better Auth integration.
    """
    def __init__(
        self,
        id: str = "system",
        email: str = "system@local",
        name: str = "System",
        role: str = "admin"
    ):
        self.id = id
        self.email = email
        self.name = name
        self.role = role


async def get_current_user(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
) -> CurrentUser:
    """
    Get current authenticated user.
    
    Currently uses headers for user info (placeholder).
    Will be replaced with Better Auth JWT validation.
    """
    # Placeholder - accept any user from headers or default to admin
    return CurrentUser(
        id=x_user_id or "admin",
        email=x_user_email or "admin@local",
        name="Admin",
        role="admin"
    )


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Get current active (non-disabled) user.
    """
    # Placeholder - will add is_active check with Better Auth
    return current_user


async def require_admin(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Require admin role for endpoint.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# ==================== Validation Helpers ====================

def validate_claim_exists(claim_id: int, db: Session) -> None:
    """
    Validate that a claim exists.
    Raises HTTPException if not found.
    """
    from app.db import models
    
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found"
        )


def validate_claim_status(claim_id: int, required_status: str, db: Session) -> None:
    """
    Validate that a claim is in the required status.
    Raises HTTPException if not.
    """
    from app.db import models
    
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found"
        )
    
    if claim.status != required_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Claim is not in {required_status} status (current: {claim.status})"
        )


# ==================== Pagination ====================

class PaginationParams:
    """Common pagination parameters."""
    
    def __init__(
        self,
        skip: int = 0,
        limit: int = 100
    ):
        self.skip = max(0, skip)
        self.limit = min(500, max(1, limit))


def get_pagination(
    skip: int = 0,
    limit: int = 100
) -> PaginationParams:
    """Get pagination parameters with validation."""
    return PaginationParams(skip=skip, limit=limit)

