"""
Base schemas and common enums for API v1.
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Any
from enum import Enum


class BaseSchema(BaseModel):
    """Base schema with ORM mode enabled."""
    model_config = ConfigDict(from_attributes=True)


class TimestampMixin(BaseModel):
    """Mixin for models with timestamps."""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ==================== Enums ====================

class ClaimStatus(str, Enum):
    """Claim processing status."""
    PROCESSING = "PROCESSING"
    OCR_REVIEW = "OCR_REVIEW"
    CLEANING = "CLEANING"
    ANONYMIZING = "ANONYMIZING"
    ANONYMIZATION_REVIEW = "ANONYMIZATION_REVIEW"
    READY_FOR_ANALYSIS = "READY_FOR_ANALYSIS"
    ANALYZING = "ANALYZING"
    ANALYZED = "ANALYZED"
    FAILED = "FAILED"
    # Legacy statuses
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    APPROVED = "APPROVED"


class Country(str, Enum):
    """Supported countries."""
    SK = "SK"
    IT = "IT"
    DE = "DE"


class RAGDocumentType(str, Enum):
    """RAG document types."""
    GENERAL = "general"
    HEALTH = "zdravotne"
    LIFE = "zivotne"
    PROPERTY = "majetkove"
    VEHICLE = "vozidlove"
    TRAVEL = "cestovne"


# ==================== Common Response Schemas ====================

class MessageResponse(BaseModel):
    """Standard success message response."""
    message: str


class MessageWithIdResponse(MessageResponse):
    """Success response with ID."""
    id: int


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    code: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Base for paginated responses."""
    total: int
    skip: int
    limit: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    services: dict[str, str]

