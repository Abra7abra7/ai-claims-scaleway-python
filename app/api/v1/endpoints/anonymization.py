"""
Anonymization Review HITL (Human-in-the-Loop) endpoints.
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
    AnonReviewResponse,
    AnonReviewDocument,
    AnonEditRequest
)
from app.api.v1.schemas.claims import RetryResponse, StatusResetResponse
from app.api.v1.schemas.base import MessageResponse
from app.db import models
from app.services.audit import AuditLogger

router = APIRouter()


@router.get(
    "",
    response_model=AnonReviewResponse,
    summary="Get anonymization review data",
    description="Get claim documents for anonymization review"
)
def get_anon_review(
    claim_id: int,
    db: Session = Depends(get_database)
):
    """
    Get claim documents ready for anonymization review.
    """
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    if claim.status != models.ClaimStatus.ANONYMIZATION_REVIEW.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Claim is not in ANONYMIZATION_REVIEW status (current: {claim.status})"
        )
    
    return AnonReviewResponse(
        claim_id=claim.id,
        country=claim.country,
        documents=[
            AnonReviewDocument(
                id=doc.id,
                filename=doc.filename,
                cleaned_text=doc.cleaned_text,
                anonymized_text=doc.anonymized_text
            )
            for doc in claim.documents
        ]
    )


@router.post(
    "/edit",
    response_model=MessageResponse,
    summary="Edit anonymized text",
    description="Edit anonymized text for one or more documents"
)
def edit_anon(
    claim_id: int,
    request: AnonEditRequest,
    db: Session = Depends(get_database),
    audit: AuditLogger = Depends(get_audit_logger),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Edit anonymized text for documents.
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
            old_text = document.anonymized_text
            document.anonymized_text = new_text
            document.anon_reviewed_by = current_user.id
            document.anon_reviewed_at = models.datetime.utcnow()
            
            # Log edit
            audit.log_anon_edit(
                user=current_user.id,
                document_id=doc_id,
                old_text=old_text or "",
                new_text=new_text,
                db=db
            )
    
    db.commit()
    return MessageResponse(message="Anonymized text updated")


@router.post(
    "/approve",
    response_model=MessageResponse,
    summary="Approve anonymization",
    description="Approve anonymization results and set ready for analysis"
)
def approve_anon(
    claim_id: int,
    db: Session = Depends(get_database),
    audit: AuditLogger = Depends(get_audit_logger),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Approve anonymization and set ready for analysis.
    """
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    if claim.status != models.ClaimStatus.ANONYMIZATION_REVIEW.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Claim is not in ANONYMIZATION_REVIEW status"
        )
    
    # Mark documents as reviewed
    for doc in claim.documents:
        if not doc.anon_reviewed_by:
            doc.anon_reviewed_by = current_user.id
            doc.anon_reviewed_at = models.datetime.utcnow()
    
    # Log approval
    audit.log_anon_approval(
        user=current_user.id,
        claim_id=claim.id,
        db=db
    )
    
    # Update status
    claim.status = models.ClaimStatus.READY_FOR_ANALYSIS.value
    db.commit()
    
    return MessageResponse(message="Anonymization approved, ready for analysis")


@router.post(
    "/re-clean",
    response_model=MessageResponse,
    summary="Re-run cleaning",
    description="Re-run cleaning process for a claim"
)
def re_clean_claim(
    claim_id: int,
    db: Session = Depends(get_database),
    audit: AuditLogger = Depends(get_audit_logger),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Re-run cleaning for a claim (useful after cleaner improvements).
    Also triggers re-anonymization.
    """
    from app.worker import clean_document
    
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    # Reset cleaned and anonymized text
    for doc in claim.documents:
        doc.cleaned_text = None
        doc.anonymized_text = None
    
    # Set status to cleaning
    claim.status = models.ClaimStatus.CLEANING.value
    db.commit()
    
    # Log action
    audit.log(
        user=current_user.id,
        action="RE_CLEAN",
        entity_type="Claim",
        entity_id=claim_id,
        db=db
    )
    
    # Trigger cleaning tasks
    for doc in claim.documents:
        clean_document.delay(doc.id)
    
    return MessageResponse(message=f"Re-cleaning started for claim {claim_id}")


@router.post(
    "/retry",
    response_model=RetryResponse,
    summary="Retry anonymization",
    description="Retry anonymization for stuck claims"
)
def retry_anonymization(
    claim_id: int,
    db: Session = Depends(get_database),
    audit: AuditLogger = Depends(get_audit_logger),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Retry anonymization for claims stuck in ANONYMIZING or CLEANING state.
    """
    from app.worker import anonymize_document, clean_document
    
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    if claim.status not in [models.ClaimStatus.ANONYMIZING.value, models.ClaimStatus.CLEANING.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Claim is in {claim.status} status. Retry only works for ANONYMIZING or CLEANING status."
        )
    
    # Find documents that need retry
    docs_to_retry = []
    for doc in claim.documents:
        if claim.status == models.ClaimStatus.ANONYMIZING.value:
            if doc.cleaned_text and not doc.anonymized_text:
                docs_to_retry.append(doc)
        elif claim.status == models.ClaimStatus.CLEANING.value:
            if doc.original_text and not doc.cleaned_text:
                docs_to_retry.append(doc)
    
    if not docs_to_retry:
        return RetryResponse(
            message="No documents need retry",
            count=0,
            claim_id=claim_id,
            status=claim.status
        )
    
    # Trigger tasks
    if claim.status == models.ClaimStatus.ANONYMIZING.value:
        for doc in docs_to_retry:
            anonymize_document.delay(doc.id, claim.country)
            audit.log(
                user=current_user.id,
                action="ANONYMIZATION_RETRY",
                entity_type="ClaimDocument",
                entity_id=doc.id,
                db=db
            )
    else:
        for doc in docs_to_retry:
            clean_document.delay(doc.id)
            audit.log(
                user=current_user.id,
                action="CLEANING_RETRY",
                entity_type="ClaimDocument",
                entity_id=doc.id,
                db=db
            )
    
    return RetryResponse(
        message=f"Retry triggered for {len(docs_to_retry)} documents",
        count=len(docs_to_retry),
        claim_id=claim_id,
        status=claim.status
    )


@router.post(
    "/reset-status",
    response_model=StatusResetResponse,
    summary="Reset claim status",
    description="Reset claim status to READY_FOR_ANALYSIS"
)
def reset_claim_status(
    claim_id: int,
    db: Session = Depends(get_database),
    audit: AuditLogger = Depends(get_audit_logger),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Reset claim status from ANALYZING/FAILED to READY_FOR_ANALYSIS.
    """
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    allowed_statuses = [
        models.ClaimStatus.ANALYZING.value,
        models.ClaimStatus.FAILED.value,
        models.ClaimStatus.ANALYZED.value
    ]
    
    if claim.status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reset status from {claim.status}. Only allowed from ANALYZING, FAILED or ANALYZED."
        )
    
    old_status = claim.status
    claim.status = models.ClaimStatus.READY_FOR_ANALYSIS.value
    db.commit()
    
    audit.log(
        user=current_user.id,
        action="STATUS_RESET",
        entity_type="Claim",
        entity_id=claim_id,
        changes={"from": old_status, "to": claim.status},
        db=db
    )
    
    return StatusResetResponse(
        message=f"Claim status reset",
        old_status=old_status,
        new_status=claim.status
    )

