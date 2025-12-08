"""
Claim-related schemas for API v1.
"""
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from .base import BaseSchema, ClaimStatus, Country, PaginatedResponse
from .documents import DocumentResponse, DocumentSummary


# ==================== Request Schemas ====================

class ClaimUploadRequest(BaseModel):
    """Request for claim upload (query params)."""
    country: Country = Field(
        default=Country.SK,
        description="Country code for the claim"
    )


class ClaimUpdateRequest(BaseModel):
    """Request to update claim metadata."""
    country: Optional[Country] = None
    status: Optional[ClaimStatus] = None


class AnalyzeRequest(BaseModel):
    """Request to start analysis."""
    prompt_id: str = Field(
        default="default",
        description="ID of the prompt template to use"
    )


# ==================== Response Schemas ====================

class ClaimBase(BaseSchema):
    """Base claim schema."""
    id: int
    country: str
    status: ClaimStatus
    created_at: Optional[datetime] = None


class ClaimSummary(ClaimBase):
    """Minimal claim info for list endpoints."""
    document_count: int = Field(default=0, description="Number of documents")


class ClaimDetail(ClaimBase):
    """Full claim detail with all fields."""
    analysis_result: Optional[Any] = None
    analysis_model: Optional[str] = None
    documents: list[DocumentResponse] = []


class ClaimListResponse(PaginatedResponse):
    """Paginated list of claims."""
    items: list[ClaimSummary]


class ClaimUploadResponse(BaseModel):
    """Response after uploading a new claim."""
    id: int
    country: str
    status: str
    message: str
    document_count: int


# ==================== Retry Schemas ====================

class RetryResponse(BaseModel):
    """Response for retry operations."""
    message: str
    count: int
    claim_id: int
    status: str


class StatusResetResponse(BaseModel):
    """Response for status reset."""
    message: str
    old_status: str
    new_status: str

