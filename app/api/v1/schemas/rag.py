"""
RAG (Retrieval-Augmented Generation) schemas for API v1.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .base import BaseSchema, Country, RAGDocumentType


# ==================== Request Schemas ====================

class RAGUploadRequest(BaseModel):
    """Request for RAG document upload (query params)."""
    country: Country = Field(
        default=Country.SK,
        description="Country code"
    )
    document_type: RAGDocumentType = Field(
        default=RAGDocumentType.GENERAL,
        description="Type of policy document"
    )


# ==================== Response Schemas ====================

class RAGDocumentBase(BaseSchema):
    """Base RAG document schema."""
    id: int
    filename: str
    country: str
    document_type: str
    # Alias for frontend compatibility
    category: Optional[str] = None  


class RAGDocumentSummary(RAGDocumentBase):
    """Summary for list endpoints."""
    uploaded_by: Optional[str] = None
    created_at: Optional[datetime] = None
    is_processed: bool = False
    chunk_count: int = 0


class RAGDocumentDetail(RAGDocumentBase):
    """Full RAG document detail."""
    s3_key: str
    text_content: Optional[str] = None
    uploaded_by: Optional[str] = None
    created_at: Optional[datetime] = None


class RAGDocumentListResponse(BaseModel):
    """List of RAG documents."""
    items: list[RAGDocumentSummary]
    total: int


class RAGUploadResponse(BaseModel):
    """Response after uploading RAG document."""
    id: int
    message: str


class RAGFolderStructure(BaseModel):
    """Folder structure for RAG documents."""
    countries: dict[str, dict[str, list[str]]]


# ==================== Query Schemas ====================

class RAGQueryRequest(BaseModel):
    """Request to query RAG documents."""
    query: str = Field(..., description="Query text")
    country: Optional[Country] = None
    document_type: Optional[RAGDocumentType] = None
    limit: int = Field(default=5, ge=1, le=20)


class RAGQueryResult(BaseModel):
    """Single RAG query result."""
    document_id: int
    filename: str
    relevance_score: float
    snippet: str


class RAGQueryResponse(BaseModel):
    """Response for RAG query."""
    query: str
    results: list[RAGQueryResult]

