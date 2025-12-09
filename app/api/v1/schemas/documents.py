"""
Document-related schemas for API v1.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .base import BaseSchema


# ==================== Document Schemas ====================

class DocumentBase(BaseSchema):
    """Base document schema."""
    id: int
    filename: str
    s3_key: str


class DocumentSummary(DocumentBase):
    """Minimal document info for lists."""
    pass


class DocumentResponse(DocumentBase):
    """Full document response with all fields."""
    original_text: Optional[str] = None
    cleaned_text: Optional[str] = None
    anonymized_text: Optional[str] = None
    ocr_reviewed_by: Optional[str] = None
    ocr_reviewed_at: Optional[datetime] = None
    anon_reviewed_by: Optional[str] = None
    anon_reviewed_at: Optional[datetime] = None


class DocumentTextOnly(BaseModel):
    """Document with text fields only."""
    id: int
    filename: str
    original_text: Optional[str] = None
    cleaned_text: Optional[str] = None
    anonymized_text: Optional[str] = None


# ==================== OCR Review Schemas ====================

class OCRReviewDocument(BaseModel):
    """Document for OCR review."""
    id: int
    filename: str
    original_text: Optional[str] = None


class OCRReviewResponse(BaseModel):
    """OCR review response."""
    claim_id: int
    country: str
    documents: list[OCRReviewDocument]


class OCREditRequest(BaseModel):
    """Request to edit OCR text. Keys are document IDs as strings."""
    edits: dict[str, str] = Field(
        ...,
        description="Map of document_id (as string) to new text",
        examples=[{"1": "Corrected OCR text", "2": "Another corrected text"}]
    )


# ==================== Cleaning Preview Schemas ====================

class CleaningStats(BaseModel):
    """Statistics for text cleaning."""
    original_length: int
    cleaned_length: int
    characters_removed: int
    reduction_percent: float
    original_lines: int
    cleaned_lines: int


class CleaningPreviewDocument(BaseModel):
    """Single document cleaning preview."""
    id: int
    filename: str
    original_text: str
    cleaned_text: str
    stats: CleaningStats


class CleaningPreviewResponse(BaseModel):
    """Response for cleaning preview."""
    claim_id: int
    documents: list[CleaningPreviewDocument]
    total_stats: dict


class CleaningTextRequest(BaseModel):
    """Request to preview cleaning for single text."""
    text: str = Field(..., description="Raw text to clean")


class CleaningTextResponse(BaseModel):
    """Response for single text cleaning preview."""
    original_text: str
    cleaned_text: str
    stats: CleaningStats


class CleanedEditRequest(BaseModel):
    """Request to edit cleaned text. Keys are document IDs as strings."""
    edits: dict[str, str] = Field(
        ...,
        description="Map of document_id (as string) to new cleaned text",
        examples=[{"1": "Edited cleaned text", "2": "Another edited text"}]
    )


# ==================== Anonymization Review Schemas ====================

class AnonReviewDocument(BaseModel):
    """Document for anonymization review."""
    id: int
    filename: str
    cleaned_text: Optional[str] = None
    anonymized_text: Optional[str] = None


class AnonReviewResponse(BaseModel):
    """Anonymization review response."""
    claim_id: int
    country: str
    documents: list[AnonReviewDocument]


class AnonEditRequest(BaseModel):
    """Request to edit anonymized text. Keys are document IDs as strings."""
    edits: dict[str, str] = Field(
        ...,
        description="Map of document_id (as string) to new anonymized text",
        examples=[{"1": "Edited <OSOBA> text"}]
    )

