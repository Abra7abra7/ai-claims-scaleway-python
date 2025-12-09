from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
import enum
from datetime import datetime

Base = declarative_base()

class ClaimStatus(str, enum.Enum):
    PROCESSING = "PROCESSING"
    OCR_REVIEW = "OCR_REVIEW"
    CLEANING = "CLEANING"
    ANONYMIZING = "ANONYMIZING"
    ANONYMIZATION_REVIEW = "ANONYMIZATION_REVIEW"
    READY_FOR_ANALYSIS = "READY_FOR_ANALYSIS"
    ANALYZING = "ANALYZING"
    ANALYZED = "ANALYZED"
    FAILED = "FAILED"
    # Legacy statuses (keeping for backward compatibility)
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    APPROVED = "APPROVED"

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    country = Column(String, nullable=False, default="SK")  # SK, IT, DE
    status = Column(String, default=ClaimStatus.PROCESSING.value)
    analysis_result = Column(JSONB, nullable=True)
    analysis_model = Column(String, nullable=True)  # Model used for analysis
    
    documents = relationship("ClaimDocument", back_populates="claim", cascade="all, delete-orphan")
    reports = relationship("AnalysisReport", back_populates="claim", cascade="all, delete-orphan")

class ClaimDocument(Base):
    __tablename__ = "claim_documents"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"))
    filename = Column(String)
    s3_key = Column(String)
    original_text = Column(Text, nullable=True)  # OCR output
    cleaned_text = Column(Text, nullable=True)  # After cleaning
    anonymized_text = Column(Text, nullable=True)  # After anonymization
    embedding = Column(Vector(1024), nullable=True)
    
    # HITL review tracking
    ocr_reviewed_by = Column(String, nullable=True)
    ocr_reviewed_at = Column(DateTime, nullable=True)
    anon_reviewed_by = Column(String, nullable=True)
    anon_reviewed_at = Column(DateTime, nullable=True)

    claim = relationship("Claim", back_populates="documents")


class RAGDocument(Base):
    __tablename__ = "rag_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)
    country = Column(String, nullable=False)  # SK, IT, DE
    document_type = Column(String, nullable=False)  # vseobecne-podmienky, zdravotne, etc.
    text_content = Column(Text, nullable=True)
    embedding = Column(Vector(1024), nullable=True)
    uploaded_by = Column(String, nullable=True)  # admin username
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, nullable=False)  # admin username
    action = Column(String, nullable=False)  # OCR_EDITED, ANON_APPROVED, etc.
    entity_type = Column(String, nullable=False)  # Claim, ClaimDocument, RAGDocument
    entity_id = Column(Integer, nullable=False)
    changes = Column(JSONB, nullable=True)  # {"old_value": "...", "new_value": "..."}
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"))
    s3_key = Column(String, nullable=False)  # claims/{id}/reports/analysis_{timestamp}.pdf
    model_used = Column(String, nullable=True)  # mistral-small-latest, etc.
    prompt_id = Column(String, nullable=True)  # default, fraud_detection, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="reports")


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    template = Column(Text, nullable=False)
    llm_model = Column(String, default="mistral-small-latest")
    created_at = Column(DateTime, default=datetime.utcnow)


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default=UserRole.USER.value)
    locale = Column(String, default="sk")  # sk, en
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")


class UserSession(Base):
    """User session for tracking active logins."""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    
    # Session metadata for audit
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    
    # Revocation
    is_revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime, nullable=True)
    revoked_reason = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
