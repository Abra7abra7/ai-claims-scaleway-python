"""
Reports endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from app.api.deps import (
    get_database,
    get_storage_service
)
from app.api.v1.schemas.reports import (
    ReportSummary,
    ReportListResponse,
    ReportDownloadResponse
)
from app.db import models
from app.services.storage import StorageService

router = APIRouter()


@router.get(
    "/claims/{claim_id}",
    response_model=ReportListResponse,
    summary="Get claim reports",
    description="Get all reports for a specific claim"
)
def get_claim_reports(
    claim_id: int,
    db: Session = Depends(get_database)
):
    """
    Get all reports for a claim.
    """
    # Check claim exists
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    reports = db.query(models.AnalysisReport).filter(
        models.AnalysisReport.claim_id == claim_id
    ).order_by(models.AnalysisReport.created_at.desc()).all()
    
    return ReportListResponse(
        claim_id=claim_id,
        reports=[
            ReportSummary(
                id=report.id,
                claim_id=report.claim_id,
                s3_key=report.s3_key,
                model_used=report.model_used,
                prompt_id=report.prompt_id,
                created_at=report.created_at
            )
            for report in reports
        ],
        total=len(reports)
    )


@router.get(
    "/{report_id}",
    response_model=ReportSummary,
    summary="Get report details",
    description="Get details of a specific report"
)
def get_report(
    report_id: int,
    db: Session = Depends(get_database)
):
    """
    Get report details.
    """
    report = db.query(models.AnalysisReport).filter(
        models.AnalysisReport.id == report_id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return ReportSummary(
        id=report.id,
        claim_id=report.claim_id,
        s3_key=report.s3_key,
        model_used=report.model_used,
        prompt_id=report.prompt_id,
        created_at=report.created_at
    )


@router.get(
    "/{report_id}/download",
    summary="Download report",
    description="Stream report PDF directly from storage"
)
def download_report(
    report_id: int,
    db: Session = Depends(get_database),
    storage: StorageService = Depends(get_storage_service)
):
    """
    Stream report PDF directly from MinIO to browser.
    """
    report = db.query(models.AnalysisReport).filter(
        models.AnalysisReport.id == report_id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    try:
        # Download file from MinIO
        file_content = storage.download_bytes(report.s3_key)
        
        # Generate filename from s3_key
        filename = report.s3_key.split('/')[-1]
        
        # Stream to browser
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "public, max-age=3600"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve report: {str(e)}"
        )

