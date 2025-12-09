"""
Statistics and dashboard schemas for API v1.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ==================== Dashboard Stats ====================

class ClaimCountByStatus(BaseModel):
    """Claim count grouped by status."""
    status: str
    count: int


class ClaimCountByCountry(BaseModel):
    """Claim count grouped by country."""
    country: str
    count: int


class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_claims: int
    claims_by_status: list[ClaimCountByStatus]
    claims_by_country: list[ClaimCountByCountry]
    pending_ocr_review: int
    pending_anon_review: int
    pending_analysis: int
    completed_today: int
    failed_count: int


# ==================== Claim Statistics ====================

class ClaimProcessingStats(BaseModel):
    """Processing statistics for claims."""
    total_documents: int
    total_characters_processed: int
    average_processing_time_seconds: Optional[float] = None
    success_rate: float


class TimeRangeStats(BaseModel):
    """Statistics for a time range."""
    start_date: datetime
    end_date: datetime
    claims_created: int
    claims_completed: int
    claims_failed: int


class ClaimStatsResponse(BaseModel):
    """Complete claim statistics response."""
    processing: ClaimProcessingStats
    by_status: list[ClaimCountByStatus]
    by_country: list[ClaimCountByCountry]
    last_7_days: Optional[TimeRangeStats] = None
    last_30_days: Optional[TimeRangeStats] = None


# ==================== System Stats ====================

class SystemHealth(BaseModel):
    """System health information."""
    database: str
    redis: str
    storage: str
    presidio: str
    worker: str


class SystemStatsResponse(BaseModel):
    """System statistics."""
    health: SystemHealth
    uptime_seconds: int
    version: str
    rag_documents_count: int
    total_storage_bytes: Optional[int] = None

