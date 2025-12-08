"""
Report schemas for API v1.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .base import BaseSchema


# ==================== Report Schemas ====================

class ReportBase(BaseSchema):
    """Base report schema."""
    id: int
    claim_id: int
    s3_key: str
    created_at: Optional[datetime] = None


class ReportSummary(ReportBase):
    """Summary for list endpoints."""
    model_used: Optional[str] = None
    prompt_id: Optional[str] = None


class ReportDetail(ReportBase):
    """Full report detail."""
    model_used: Optional[str] = None
    prompt_id: Optional[str] = None


class ReportListResponse(BaseModel):
    """List of reports for a claim."""
    claim_id: int
    reports: list[ReportSummary]
    total: int


class ReportDownloadResponse(BaseModel):
    """Response with download URL."""
    download_url: str
    expires_in: int = Field(
        default=3600,
        description="URL expiration time in seconds"
    )


# ==================== Report Generation ====================

class GenerateReportRequest(BaseModel):
    """Request to generate a new report."""
    prompt_id: str = Field(
        default="default",
        description="Prompt template ID"
    )
    format: str = Field(
        default="pdf",
        description="Output format (pdf, json)"
    )


class GenerateReportResponse(BaseModel):
    """Response after starting report generation."""
    report_id: int
    message: str
    status: str

