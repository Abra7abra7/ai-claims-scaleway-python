"""
Authentication service for user management and session handling.
Designed for regulated environments (insurance) with full audit logging.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import secrets
import hashlib
import os

from sqlalchemy.orm import Session
from fastapi import Request

from app.db.models import User, UserSession, UserRole
from app.services.audit import AuditLogger


# Password hashing using PBKDF2 (secure and standard)
SALT_LENGTH = 32
ITERATIONS = 100000
KEY_LENGTH = 64


def hash_password(password: str) -> str:
    """Hash password using PBKDF2-SHA256."""
    salt = os.urandom(SALT_LENGTH)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        ITERATIONS,
        dklen=KEY_LENGTH
    )
    return f"{salt.hex()}:{key.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    try:
        salt_hex, key_hex = password_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        stored_key = bytes.fromhex(key_hex)
        
        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            ITERATIONS,
            dklen=KEY_LENGTH
        )
        return secrets.compare_digest(new_key, stored_key)
    except Exception:
        return False


def generate_session_token() -> str:
    """Generate secure random session token."""
    return secrets.token_urlsafe(64)


class AuthService:
    """
    Authentication service with full audit logging.
    Handles user registration, login, logout, and session management.
    """
    
    # Session settings
    SESSION_DURATION_HOURS = 24 * 7  # 7 days
    SESSION_INACTIVITY_HOURS = 24  # Expire after 24h inactivity
    
    def __init__(self):
        self.audit = AuditLogger()
    
    def register_user(
        self,
        db: Session,
        email: str,
        password: str,
        name: str,
        role: str = UserRole.USER.value,
        locale: str = "sk",
        request: Optional[Request] = None
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Register a new user.
        
        Returns:
            Tuple of (User, None) on success or (None, error_message) on failure.
        """
        # Check if email already exists
        existing = db.query(User).filter(User.email == email.lower()).first()
        if existing:
            # Log failed registration attempt
            self._log_auth_action(
                db=db,
                action="REGISTER_FAILED",
                user_email=email,
                request=request,
                details={"reason": "email_exists"}
            )
            return None, "Email already registered"
        
        # Validate password strength
        if len(password) < 8:
            return None, "Password must be at least 8 characters"
        
        # Create user
        user = User(
            email=email.lower().strip(),
            password_hash=hash_password(password),
            name=name.strip(),
            role=role,
            locale=locale,
            is_active=True,
            email_verified=False
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Log successful registration
        self._log_auth_action(
            db=db,
            action="REGISTER_SUCCESS",
            user_email=email,
            user_id=user.id,
            request=request,
            details={"role": role, "locale": locale}
        )
        
        return user, None
    
    def login(
        self,
        db: Session,
        email: str,
        password: str,
        request: Optional[Request] = None
    ) -> Tuple[Optional[UserSession], Optional[str]]:
        """
        Authenticate user and create session.
        
        Returns:
            Tuple of (UserSession, None) on success or (None, error_message) on failure.
        """
        # Find user
        user = db.query(User).filter(User.email == email.lower()).first()
        
        if not user:
            # Log failed login - user not found
            self._log_auth_action(
                db=db,
                action="LOGIN_FAILED",
                user_email=email,
                request=request,
                details={"reason": "user_not_found"}
            )
            return None, "Invalid email or password"
        
        # Check if user is active
        if not user.is_active:
            self._log_auth_action(
                db=db,
                action="LOGIN_FAILED",
                user_email=email,
                user_id=user.id,
                request=request,
                details={"reason": "account_disabled"}
            )
            return None, "Account is disabled"
        
        # Verify password
        if not verify_password(password, user.password_hash):
            self._log_auth_action(
                db=db,
                action="LOGIN_FAILED",
                user_email=email,
                user_id=user.id,
                request=request,
                details={"reason": "invalid_password"}
            )
            return None, "Invalid email or password"
        
        # Create session
        session = self._create_session(db, user, request)
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        db.commit()
        
        # Log successful login
        self._log_auth_action(
            db=db,
            action="LOGIN_SUCCESS",
            user_email=email,
            user_id=user.id,
            request=request,
            details={"session_id": session.id}
        )
        
        return session, None
    
    def logout(
        self,
        db: Session,
        session_token: str,
        request: Optional[Request] = None
    ) -> bool:
        """
        Logout user by revoking session.
        
        Returns:
            True if logout successful, False if session not found.
        """
        session = db.query(UserSession).filter(
            UserSession.token == session_token,
            UserSession.is_revoked == False
        ).first()
        
        if not session:
            return False
        
        # Revoke session
        session.is_revoked = True
        session.revoked_at = datetime.utcnow()
        session.revoked_reason = "user_logout"
        db.commit()
        
        # Log logout
        self._log_auth_action(
            db=db,
            action="LOGOUT",
            user_email=session.user.email,
            user_id=session.user_id,
            request=request,
            details={"session_id": session.id}
        )
        
        return True
    
    def validate_session(
        self,
        db: Session,
        session_token: str
    ) -> Optional[User]:
        """
        Validate session token and return user if valid.
        Also updates last activity timestamp.
        
        Returns:
            User if session is valid, None otherwise.
        """
        session = db.query(UserSession).filter(
            UserSession.token == session_token,
            UserSession.is_revoked == False
        ).first()
        
        if not session:
            return None
        
        now = datetime.utcnow()
        
        # Check if session expired
        if session.expires_at < now:
            session.is_revoked = True
            session.revoked_at = now
            session.revoked_reason = "expired"
            db.commit()
            return None
        
        # Check inactivity timeout
        inactivity_limit = session.last_activity_at + timedelta(hours=self.SESSION_INACTIVITY_HOURS)
        if inactivity_limit < now:
            session.is_revoked = True
            session.revoked_at = now
            session.revoked_reason = "inactivity"
            db.commit()
            return None
        
        # Check if user is still active
        if not session.user.is_active:
            session.is_revoked = True
            session.revoked_at = now
            session.revoked_reason = "user_disabled"
            db.commit()
            return None
        
        # Update last activity
        session.last_activity_at = now
        db.commit()
        
        return session.user
    
    def get_user_sessions(
        self,
        db: Session,
        user_id: int,
        include_revoked: bool = False
    ) -> list[UserSession]:
        """Get all sessions for a user."""
        query = db.query(UserSession).filter(UserSession.user_id == user_id)
        
        if not include_revoked:
            query = query.filter(UserSession.is_revoked == False)
            query = query.filter(UserSession.expires_at > datetime.utcnow())
        
        return query.order_by(UserSession.created_at.desc()).all()
    
    def revoke_session(
        self,
        db: Session,
        session_id: int,
        reason: str = "admin_revoked",
        admin_user: Optional[str] = None,
        request: Optional[Request] = None
    ) -> bool:
        """Revoke a specific session (admin action)."""
        session = db.query(UserSession).filter(UserSession.id == session_id).first()
        
        if not session or session.is_revoked:
            return False
        
        session.is_revoked = True
        session.revoked_at = datetime.utcnow()
        session.revoked_reason = reason
        db.commit()
        
        # Log session revocation
        self._log_auth_action(
            db=db,
            action="SESSION_REVOKED",
            user_email=session.user.email,
            user_id=session.user_id,
            request=request,
            details={
                "session_id": session.id,
                "reason": reason,
                "revoked_by": admin_user
            }
        )
        
        return True
    
    def revoke_all_user_sessions(
        self,
        db: Session,
        user_id: int,
        reason: str = "all_sessions_revoked",
        admin_user: Optional[str] = None,
        request: Optional[Request] = None
    ) -> int:
        """Revoke all active sessions for a user. Returns count of revoked sessions."""
        sessions = db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_revoked == False
        ).all()
        
        count = 0
        now = datetime.utcnow()
        
        for session in sessions:
            session.is_revoked = True
            session.revoked_at = now
            session.revoked_reason = reason
            count += 1
        
        db.commit()
        
        if count > 0:
            user = db.query(User).filter(User.id == user_id).first()
            self._log_auth_action(
                db=db,
                action="ALL_SESSIONS_REVOKED",
                user_email=user.email if user else "unknown",
                user_id=user_id,
                request=request,
                details={
                    "sessions_revoked": count,
                    "reason": reason,
                    "revoked_by": admin_user
                }
            )
        
        return count
    
    def change_password(
        self,
        db: Session,
        user: User,
        old_password: str,
        new_password: str,
        request: Optional[Request] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Change user password.
        
        Returns:
            Tuple of (success, error_message).
        """
        # Verify old password
        if not verify_password(old_password, user.password_hash):
            self._log_auth_action(
                db=db,
                action="PASSWORD_CHANGE_FAILED",
                user_email=user.email,
                user_id=user.id,
                request=request,
                details={"reason": "invalid_old_password"}
            )
            return False, "Current password is incorrect"
        
        # Validate new password
        if len(new_password) < 8:
            return False, "New password must be at least 8 characters"
        
        # Update password
        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        
        # Log password change
        self._log_auth_action(
            db=db,
            action="PASSWORD_CHANGED",
            user_email=user.email,
            user_id=user.id,
            request=request,
            details={}
        )
        
        return True, None
    
    def _create_session(
        self,
        db: Session,
        user: User,
        request: Optional[Request] = None
    ) -> UserSession:
        """Create a new session for user."""
        now = datetime.utcnow()
        
        session = UserSession(
            user_id=user.id,
            token=generate_session_token(),
            ip_address=self._get_client_ip(request) if request else None,
            user_agent=request.headers.get("User-Agent", "")[:500] if request else None,
            created_at=now,
            expires_at=now + timedelta(hours=self.SESSION_DURATION_HOURS),
            last_activity_at=now
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Extract client IP from request, handling proxies."""
        if not request:
            return None
        
        # Check for forwarded headers (reverse proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct connection
        if request.client:
            return request.client.host
        
        return None
    
    def _log_auth_action(
        self,
        db: Session,
        action: str,
        user_email: str,
        request: Optional[Request] = None,
        user_id: Optional[int] = None,
        details: Optional[dict] = None
    ):
        """Log authentication action to audit log."""
        changes = {
            "email": user_email,
            **(details or {})
        }
        
        if request:
            changes["ip_address"] = self._get_client_ip(request)
            changes["user_agent"] = request.headers.get("User-Agent", "")[:200]
        
        self.audit.log(
            user=user_email,
            action=action,
            entity_type="User",
            entity_id=user_id or 0,
            changes=changes,
            db=db
        )


# Singleton instance
auth_service = AuthService()

