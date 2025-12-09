"""
Token service for managing temporary tokens.

Handles:
- Password reset tokens
- Email verification tokens
- Token expiration
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum
import enum

from app.db.models import Base


class TokenType(str, enum.Enum):
    """Token type enumeration."""
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"


class Token(Base):
    """Token model for temporary authentication tokens."""
    __tablename__ = "auth_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    token_type = Column(SQLEnum(TokenType), nullable=False)
    user_email = Column(String, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class TokenService:
    """Service for managing authentication tokens."""
    
    @staticmethod
    def generate_token() -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)
    
    def create_password_reset_token(
        self,
        email: str,
        db: Session,
        expires_in_hours: int = 1
    ) -> str:
        """
        Create a password reset token.
        
        Args:
            email: User's email address
            db: Database session
            expires_in_hours: Token expiration time in hours (default: 1)
            
        Returns:
            Generated token string
        """
        # Invalidate any existing password reset tokens for this email
        db.query(Token).filter(
            Token.user_email == email,
            Token.token_type == TokenType.PASSWORD_RESET,
            Token.used == False
        ).update({"used": True})
        db.commit()
        
        # Create new token
        token = self.generate_token()
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        db_token = Token(
            token=token,
            token_type=TokenType.PASSWORD_RESET,
            user_email=email,
            expires_at=expires_at
        )
        
        db.add(db_token)
        db.commit()
        
        return token
    
    def create_email_verification_token(
        self,
        email: str,
        db: Session,
        expires_in_hours: int = 24
    ) -> str:
        """
        Create an email verification token.
        
        Args:
            email: User's email address
            db: Database session
            expires_in_hours: Token expiration time in hours (default: 24)
            
        Returns:
            Generated token string
        """
        # Invalidate any existing verification tokens for this email
        db.query(Token).filter(
            Token.user_email == email,
            Token.token_type == TokenType.EMAIL_VERIFICATION,
            Token.used == False
        ).update({"used": True})
        db.commit()
        
        # Create new token
        token = self.generate_token()
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        db_token = Token(
            token=token,
            token_type=TokenType.EMAIL_VERIFICATION,
            user_email=email,
            expires_at=expires_at
        )
        
        db.add(db_token)
        db.commit()
        
        return token
    
    def verify_token(
        self,
        token: str,
        token_type: TokenType,
        db: Session
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify a token and return associated email.
        
        Args:
            token: Token string to verify
            token_type: Expected token type
            db: Database session
            
        Returns:
            Tuple of (is_valid, email or None)
        """
        db_token = db.query(Token).filter(
            Token.token == token,
            Token.token_type == token_type,
            Token.used == False
        ).first()
        
        if not db_token:
            return False, None
        
        # Check if expired
        if db_token.expires_at < datetime.utcnow():
            return False, None
        
        # Mark as used
        db_token.used = True
        db.commit()
        
        return True, db_token.user_email
    
    def cleanup_expired_tokens(self, db: Session) -> int:
        """
        Clean up expired tokens from database.
        
        Args:
            db: Database session
            
        Returns:
            Number of tokens deleted
        """
        result = db.query(Token).filter(
            Token.expires_at < datetime.utcnow()
        ).delete()
        db.commit()
        
        return result


# Singleton instance
_token_service = None

def get_token_service() -> TokenService:
    """Get token service singleton."""
    global _token_service
    if _token_service is None:
        _token_service = TokenService()
    return _token_service

