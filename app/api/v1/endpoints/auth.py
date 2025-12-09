"""
Authentication API endpoints.
Provides login, logout, registration, and session management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Cookie
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.services.auth import auth_service
from app.services.email_service import get_email_service
from app.services.token_service import get_token_service, TokenType
from app.db.models import User, UserRole
from app.api.v1.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    PasswordChangeRequest,
    SessionRevokeRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailVerificationRequest,
    EmailVerificationConfirm,
    UserResponse,
    SessionResponse,
    LoginResponse,
    AuthStatusResponse,
    MessageResponse,
    SessionListResponse,
)


router = APIRouter()

# Cookie settings
COOKIE_NAME = "session_token"
COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 days in seconds


def get_session_token(session_token: Optional[str] = Cookie(None)) -> Optional[str]:
    """Extract session token from cookie."""
    return session_token


def get_current_user(
    session_token: Optional[str] = Depends(get_session_token),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current authenticated user from session token."""
    if not session_token:
        return None
    return auth_service.validate_session(db, session_token)


def require_auth(
    user: Optional[User] = Depends(get_current_user)
) -> User:
    """Require authenticated user."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return user


def require_admin(
    user: User = Depends(require_auth)
) -> User:
    """Require admin user."""
    if user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    - **email**: Valid email address (unique)
    - **password**: At least 8 characters
    - **name**: User's display name
    - **locale**: Preferred language (sk or en)
    """
    user, error = auth_service.register_user(
        db=db,
        email=data.email,
        password=data.password,
        name=data.name,
        locale=data.locale,
        request=request
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return user


@router.post("/login", response_model=LoginResponse)
async def login(
    data: UserLoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and create session.
    
    Returns session token in both response body and HTTP-only cookie.
    """
    session, error = auth_service.login(
        db=db,
        email=data.email,
        password=data.password,
        request=request
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error
        )
    
    # Set HTTP-only cookie for browser clients
    response.set_cookie(
        key=COOKIE_NAME,
        value=session.token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    return LoginResponse(
        token=session.token,
        user=UserResponse.model_validate(session.user),
        expires_at=session.expires_at
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    response: Response,
    session_token: Optional[str] = Depends(get_session_token),
    db: Session = Depends(get_db)
):
    """
    Logout current user by revoking session.
    """
    if session_token:
        auth_service.logout(db, session_token, request)
    
    # Clear cookie
    response.delete_cookie(key=COOKIE_NAME)
    
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=AuthStatusResponse)
async def get_current_user_info(
    user: Optional[User] = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    Returns authentication status and user info if authenticated.
    """
    if user:
        return AuthStatusResponse(
            authenticated=True,
            user=UserResponse.model_validate(user)
        )
    return AuthStatusResponse(authenticated=False)


@router.post("/password/change", response_model=MessageResponse)
async def change_password(
    data: PasswordChangeRequest,
    request: Request,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Change current user's password.
    
    Requires current password for verification.
    """
    success, error = auth_service.change_password(
        db=db,
        user=user,
        old_password=data.old_password,
        new_password=data.new_password,
        request=request
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return MessageResponse(message="Password changed successfully")


@router.get("/sessions", response_model=SessionListResponse)
async def get_my_sessions(
    session_token: Optional[str] = Depends(get_session_token),
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Get all active sessions for current user.
    
    Useful for "logged in devices" feature.
    """
    sessions = auth_service.get_user_sessions(db, user.id)
    
    session_list = []
    for sess in sessions:
        sess_response = SessionResponse.model_validate(sess)
        # Mark current session
        sess_response.is_current = (sess.token == session_token)
        session_list.append(sess_response)
    
    return SessionListResponse(
        sessions=session_list,
        total=len(session_list)
    )


@router.post("/sessions/{session_id}/revoke", response_model=MessageResponse)
async def revoke_session(
    session_id: int,
    request: Request,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Revoke a specific session.
    
    Users can revoke their own sessions.
    """
    # Verify session belongs to user
    from app.db.models import UserSession
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    success = auth_service.revoke_session(
        db=db,
        session_id=session_id,
        reason="user_revoked",
        admin_user=user.email,
        request=request
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to revoke session"
        )
    
    return MessageResponse(message="Session revoked successfully")


@router.post("/sessions/revoke-all", response_model=MessageResponse)
async def revoke_all_sessions(
    request: Request,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Revoke all sessions for current user (logout everywhere).
    """
    count = auth_service.revoke_all_user_sessions(
        db=db,
        user_id=user.id,
        reason="user_revoked_all",
        admin_user=user.email,
        request=request
    )
    
    return MessageResponse(message=f"Revoked {count} sessions")


# ============ Admin Endpoints ============

@router.get("/admin/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all users (admin only).
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserResponse.model_validate(u) for u in users]


@router.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get specific user details (admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.model_validate(user)


@router.post("/admin/users/{user_id}/disable", response_model=MessageResponse)
async def disable_user(
    user_id: int,
    request: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Disable user account and revoke all sessions (admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot disable your own account"
        )
    
    user.is_active = False
    
    # Revoke all sessions
    count = auth_service.revoke_all_user_sessions(
        db=db,
        user_id=user_id,
        reason="admin_disabled_account",
        admin_user=admin.email,
        request=request
    )
    
    db.commit()
    
    return MessageResponse(message=f"User disabled and {count} sessions revoked")


@router.post("/admin/users/{user_id}/enable", response_model=MessageResponse)
async def enable_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Enable user account (admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    db.commit()
    
    return MessageResponse(message="User enabled")


@router.get("/admin/users/{user_id}/sessions", response_model=SessionListResponse)
async def get_user_sessions(
    user_id: int,
    include_revoked: bool = False,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all sessions for a specific user (admin only).
    """
    sessions = auth_service.get_user_sessions(db, user_id, include_revoked)
    
    return SessionListResponse(
        sessions=[SessionResponse.model_validate(s) for s in sessions],
        total=len(sessions)
    )


@router.post("/admin/sessions/{session_id}/revoke", response_model=MessageResponse)
async def admin_revoke_session(
    session_id: int,
    data: SessionRevokeRequest,
    request: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Revoke any user session (admin only).
    """
    success = auth_service.revoke_session(
        db=db,
        session_id=session_id,
        reason=data.reason or "admin_revoked",
        admin_user=admin.email,
        request=request
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or already revoked"
        )
    
    return MessageResponse(message="Session revoked by admin")


# ==================== Password Reset ====================

@router.post(
    "/password-reset/request",
    response_model=MessageResponse,
    summary="Request password reset",
    description="Send password reset email to user"
)
async def request_password_reset(
    data: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Request password reset email.
    
    - Checks if user exists
    - Generates reset token
    - Sends email with reset link
    - Returns success even if email not found (security)
    """
    email_service = get_email_service()
    token_service = get_token_service()
    
    # Check if user exists
    user = db.query(User).filter(User.email == data.email).first()
    
    if user:
        # Generate reset token
        reset_token = token_service.create_password_reset_token(
            email=data.email,
            db=db,
            expires_in_hours=1
        )
        
        # Send email
        email_service.send_password_reset_email(
            to_email=data.email,
            reset_token=reset_token,
            user_name=user.name
        )
        
        # Log audit
        from app.services.audit import AuditLogger
        audit = AuditLogger()
        audit.log(
            db=db,
            user=data.email,
            action="PASSWORD_RESET_REQUESTED",
            entity_type="User",
            entity_id=user.id,
            changes={"ip_address": request.client.host if request.client else None}
        )
    
    # Always return success (don't reveal if email exists)
    return MessageResponse(
        message="If the email exists, a password reset link has been sent"
    )


@router.post(
    "/password-reset/confirm",
    response_model=MessageResponse,
    summary="Confirm password reset",
    description="Reset password using token from email"
)
async def confirm_password_reset(
    data: PasswordResetConfirm,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset with token.
    
    - Validates reset token
    - Updates user password
    - Revokes all user sessions (for security)
    - Returns success/error
    """
    token_service = get_token_service()
    
    # Verify token
    is_valid, email = token_service.verify_token(
        token=data.token,
        token_type=TokenType.PASSWORD_RESET,
        db=db
    )
    
    if not is_valid or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Get user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    success = auth_service.change_password(
        db=db,
        user_id=user.id,
        new_password=data.new_password,
        request=request
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )
    
    # Revoke all sessions (force re-login with new password)
    auth_service.revoke_all_user_sessions(
        db=db,
        user_id=user.id,
        reason="password_reset",
        request=request
    )
    
    # Log audit
    from app.services.audit import AuditLogger
    audit = AuditLogger()
    audit.log(
        db=db,
        user=email,
        action="PASSWORD_RESET_COMPLETED",
        entity_type="User",
        entity_id=user.id,
        changes={"ip_address": request.client.host if request.client else None}
    )
    
    return MessageResponse(message="Password reset successfully")


# ==================== Email Verification ====================

@router.post(
    "/verify-email/send",
    response_model=MessageResponse,
    summary="Send email verification",
    description="Send verification email to user"
)
async def send_verification_email(
    data: EmailVerificationRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Send email verification link.
    
    - Checks if user exists and is not verified
    - Generates verification token
    - Sends email with verification link
    """
    email_service = get_email_service()
    token_service = get_token_service()
    
    # Get user
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.email_verified:
        return MessageResponse(message="Email already verified")
    
    # Generate verification token
    verification_token = token_service.create_email_verification_token(
        email=data.email,
        db=db,
        expires_in_hours=24
    )
    
    # Send email
    email_service.send_verification_email(
        to_email=data.email,
        verification_token=verification_token,
        user_name=user.name
    )
    
    # Log audit
    from app.services.audit import AuditLogger
    audit = AuditLogger()
    audit.log(
        db=db,
        user=data.email,
        action="EMAIL_VERIFICATION_SENT",
        entity_type="User",
        entity_id=user.id
    )
    
    return MessageResponse(message="Verification email sent")


@router.get(
    "/verify-email/{token}",
    response_model=MessageResponse,
    summary="Verify email",
    description="Verify user email with token"
)
async def verify_email(
    token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Verify user email with token.
    
    - Validates verification token
    - Marks email as verified
    - Returns success/error
    """
    token_service = get_token_service()
    
    # Verify token
    is_valid, email = token_service.verify_token(
        token=token,
        token_type=TokenType.EMAIL_VERIFICATION,
        db=db
    )
    
    if not is_valid or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Get user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Mark as verified
    user.email_verified = True
    db.commit()
    
    # Log audit
    from app.services.audit import AuditLogger
    audit = AuditLogger()
    audit.log(
        db=db,
        user=email,
        action="EMAIL_VERIFIED",
        entity_type="User",
        entity_id=user.id,
        changes={"ip_address": request.client.host if request.client else None}
    )
    
    return MessageResponse(message="Email verified successfully")

