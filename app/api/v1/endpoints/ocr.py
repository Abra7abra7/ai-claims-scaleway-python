"""
OCR Review HITL (Human-in-the-Loop) endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_database,
    get_audit_logger,
    get_current_user,
    CurrentUser
)
from app.api.v1.schemas.documents import (
    OCRReviewResponse,
    OCRReviewDocument,
    OCREditRequest,
    CleaningPreviewResponse,
    CleaningPreviewDocument,
    CleaningStats,
    CleaningTextRequest,
    CleaningTextResponse
)
from app.api.v1.schemas.base import MessageResponse
from app.db import models
from app.services.cleaner import CleanerService
from app.services.audit import AuditLogger

router = APIRouter()


@router.get(
    "",
    response_model=OCRReviewResponse,
    summary="Get OCR review data",
    description="Get claim documents for OCR review"
)
def get_ocr_review(
    claim_id: int,
    db: Session = Depends(get_database)
):
    """
    Get claim documents ready for OCR review.
    """
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    if claim.status != models.ClaimStatus.OCR_REVIEW.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Claim is not in OCR_REVIEW status (current: {claim.status})"
        )
    
    return OCRReviewResponse(
        claim_id=claim.id,
        country=claim.country,
        documents=[
            OCRReviewDocument(
                id=doc.id,
                filename=doc.filename,
                original_text=doc.original_text
            )
            for doc in claim.documents
        ]
    )


@router.post(
    "/edit",
    response_model=MessageResponse,
    summary="Edit OCR text",
    description="Edit OCR extracted text for one or more documents"
)
def edit_ocr(
    claim_id: int,
    request: OCREditRequest,
    db: Session = Depends(get_database),
    audit: AuditLogger = Depends(get_audit_logger),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Edit OCR text for documents.
    """
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    for doc_id_str, new_text in request.edits.items():
        doc_id = int(doc_id_str)
        document = db.query(models.ClaimDocument).filter(
            models.ClaimDocument.id == doc_id,
            models.ClaimDocument.claim_id == claim_id
        ).first()
        
        if document:
            old_text = document.original_text
            document.original_text = new_text
            document.ocr_reviewed_by = current_user.id
            document.ocr_reviewed_at = models.datetime.utcnow()
            
            # Log edit
            audit.log_ocr_edit(
                user=current_user.id,
                document_id=doc_id,
                old_text=old_text or "",
                new_text=new_text,
                db=db
            )
    
    db.commit()
    return MessageResponse(message="OCR text updated")


@router.post(
    "/approve",
    response_model=MessageResponse,
    summary="Approve OCR",
    description="Approve OCR results and start cleaning process"
)
def approve_ocr(
    claim_id: int,
    db: Session = Depends(get_database),
    audit: AuditLogger = Depends(get_audit_logger),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Approve OCR and trigger cleaning.
    """
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    if claim.status != models.ClaimStatus.OCR_REVIEW.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Claim is not in OCR_REVIEW status"
        )
    
    # Mark documents as reviewed
    for doc in claim.documents:
        if not doc.ocr_reviewed_by:
            doc.ocr_reviewed_by = current_user.id
            doc.ocr_reviewed_at = models.datetime.utcnow()
        
        # Log approval
        audit.log_ocr_approval(
            user=current_user.id,
            document_id=doc.id,
            db=db
        )
    
    # Update status
    claim.status = models.ClaimStatus.CLEANING.value
    db.commit()
    
    # Trigger cleaning tasks
    from app.worker import clean_document
    for doc in claim.documents:
        clean_document.delay(doc.id)
    
    return MessageResponse(message="OCR approved, cleaning started")


@router.post(
    "/preview-cleaning",
    response_model=CleaningPreviewResponse,
    summary="Preview cleaning",
    description="Preview how text will look after cleaning without saving"
)
def preview_cleaning(
    claim_id: int,
    db: Session = Depends(get_database)
):
    """
    Preview cleaned text for all documents without saving.
    """
    cleaner_service = CleanerService()
    
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    results = []
    total_stats = {
        "original_total": 0,
        "cleaned_total": 0,
        "total_removed": 0,
        "reduction_percent": 0
    }
    
    for doc in claim.documents:
        original_text = doc.original_text or ""
        cleaned_text = cleaner_service.clean_text(original_text)
        stats = cleaner_service.get_cleaning_stats(original_text, cleaned_text)
        
        total_stats["original_total"] += stats["original_length"]
        total_stats["cleaned_total"] += stats["cleaned_length"]
        total_stats["total_removed"] += stats["characters_removed"]
        
        results.append(CleaningPreviewDocument(
            id=doc.id,
            filename=doc.filename,
            original_text=original_text,
            cleaned_text=cleaned_text,
            stats=CleaningStats(**stats)
        ))
    
    # Calculate total reduction
    if total_stats["original_total"] > 0:
        total_stats["reduction_percent"] = round(
            (1 - total_stats["cleaned_total"] / total_stats["original_total"]) * 100, 1
        )
    
    return CleaningPreviewResponse(
        claim_id=claim.id,
        documents=results,
        total_stats=total_stats
    )


@router.post(
    "/preview-cleaning-text",
    response_model=CleaningTextResponse,
    summary="Preview cleaning for text",
    description="Preview cleaning for a single text string"
)
def preview_cleaning_text(
    request: CleaningTextRequest
):
    """
    Preview cleaning for a single text.
    """
    cleaner_service = CleanerService()
    
    cleaned_text = cleaner_service.clean_text(request.text)
    stats = cleaner_service.get_cleaning_stats(request.text, cleaned_text)
    
    return CleaningTextResponse(
        original_text=request.text,
        cleaned_text=cleaned_text,
        stats=CleaningStats(**stats)
    )

