"""
Statistics and dashboard endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.api.deps import get_database, require_admin, CurrentUser
from app.api.v1.schemas.stats import (
    DashboardStats,
    ClaimCountByStatus,
    ClaimCountByCountry,
    ClaimStatsResponse,
    ClaimProcessingStats,
    TimeRangeStats
)
from app.db import models

router = APIRouter()


@router.get(
    "/dashboard",
    response_model=DashboardStats,
    summary="Dashboard statistics",
    description="Get statistics for the dashboard"
)
def get_dashboard_stats(
    db: Session = Depends(get_database)
):
    """
    Get dashboard statistics.
    """
    # Total claims
    total_claims = db.query(models.Claim).count()
    
    # Claims by status
    status_counts = db.query(
        models.Claim.status,
        func.count(models.Claim.id)
    ).group_by(models.Claim.status).all()
    
    claims_by_status = [
        ClaimCountByStatus(status=s, count=c)
        for s, c in status_counts
    ]
    
    # Claims by country
    country_counts = db.query(
        models.Claim.country,
        func.count(models.Claim.id)
    ).group_by(models.Claim.country).all()
    
    claims_by_country = [
        ClaimCountByCountry(country=c or "Unknown", count=cnt)
        for c, cnt in country_counts
    ]
    
    # Pending counts
    pending_ocr = db.query(models.Claim).filter(
        models.Claim.status == models.ClaimStatus.OCR_REVIEW.value
    ).count()
    
    pending_anon = db.query(models.Claim).filter(
        models.Claim.status == models.ClaimStatus.ANONYMIZATION_REVIEW.value
    ).count()
    
    pending_analysis = db.query(models.Claim).filter(
        models.Claim.status == models.ClaimStatus.READY_FOR_ANALYSIS.value
    ).count()
    
    # Completed today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    completed_today = db.query(models.Claim).filter(
        models.Claim.status == models.ClaimStatus.ANALYZED.value,
        models.Claim.created_at >= today_start
    ).count()
    
    # Failed count
    failed_count = db.query(models.Claim).filter(
        models.Claim.status == models.ClaimStatus.FAILED.value
    ).count()
    
    return DashboardStats(
        total_claims=total_claims,
        claims_by_status=claims_by_status,
        claims_by_country=claims_by_country,
        pending_ocr_review=pending_ocr,
        pending_anon_review=pending_anon,
        pending_analysis=pending_analysis,
        completed_today=completed_today,
        failed_count=failed_count
    )


@router.get(
    "/claims",
    response_model=ClaimStatsResponse,
    summary="Claim statistics",
    description="Get detailed claim processing statistics"
)
def get_claim_stats(
    db: Session = Depends(get_database),
    current_user: CurrentUser = Depends(require_admin)
):
    """
    Get detailed claim statistics.
    Admin only.
    """
    # Total documents and characters
    doc_stats = db.query(
        func.count(models.ClaimDocument.id),
        func.sum(func.length(models.ClaimDocument.original_text))
    ).first()
    
    total_docs = doc_stats[0] or 0
    total_chars = doc_stats[1] or 0
    
    # Success rate
    total_claims = db.query(models.Claim).count()
    completed_claims = db.query(models.Claim).filter(
        models.Claim.status == models.ClaimStatus.ANALYZED.value
    ).count()
    failed_claims = db.query(models.Claim).filter(
        models.Claim.status == models.ClaimStatus.FAILED.value
    ).count()
    
    success_rate = 0.0
    if total_claims > 0:
        success_rate = round(completed_claims / total_claims * 100, 2)
    
    # By status
    status_counts = db.query(
        models.Claim.status,
        func.count(models.Claim.id)
    ).group_by(models.Claim.status).all()
    
    by_status = [
        ClaimCountByStatus(status=s, count=c)
        for s, c in status_counts
    ]
    
    # By country
    country_counts = db.query(
        models.Claim.country,
        func.count(models.Claim.id)
    ).group_by(models.Claim.country).all()
    
    by_country = [
        ClaimCountByCountry(country=c or "Unknown", count=cnt)
        for c, cnt in country_counts
    ]
    
    # Last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    last_7_created = db.query(models.Claim).filter(
        models.Claim.created_at >= seven_days_ago
    ).count()
    last_7_completed = db.query(models.Claim).filter(
        models.Claim.status == models.ClaimStatus.ANALYZED.value,
        models.Claim.created_at >= seven_days_ago
    ).count()
    last_7_failed = db.query(models.Claim).filter(
        models.Claim.status == models.ClaimStatus.FAILED.value,
        models.Claim.created_at >= seven_days_ago
    ).count()
    
    # Last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    last_30_created = db.query(models.Claim).filter(
        models.Claim.created_at >= thirty_days_ago
    ).count()
    last_30_completed = db.query(models.Claim).filter(
        models.Claim.status == models.ClaimStatus.ANALYZED.value,
        models.Claim.created_at >= thirty_days_ago
    ).count()
    last_30_failed = db.query(models.Claim).filter(
        models.Claim.status == models.ClaimStatus.FAILED.value,
        models.Claim.created_at >= thirty_days_ago
    ).count()
    
    return ClaimStatsResponse(
        processing=ClaimProcessingStats(
            total_documents=total_docs,
            total_characters_processed=total_chars,
            average_processing_time_seconds=None,  # Would need to track this
            success_rate=success_rate
        ),
        by_status=by_status,
        by_country=by_country,
        last_7_days=TimeRangeStats(
            start_date=seven_days_ago,
            end_date=datetime.utcnow(),
            claims_created=last_7_created,
            claims_completed=last_7_completed,
            claims_failed=last_7_failed
        ),
        last_30_days=TimeRangeStats(
            start_date=thirty_days_ago,
            end_date=datetime.utcnow(),
            claims_created=last_30_created,
            claims_completed=last_30_completed,
            claims_failed=last_30_failed
        )
    )

