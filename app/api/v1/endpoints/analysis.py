"""
Analysis endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_database,
    get_audit_logger,
    get_current_user,
    CurrentUser
)
from app.api.v1.schemas.claims import AnalyzeRequest
from app.api.v1.schemas.base import MessageResponse
from app.db import models
from app.services.audit import AuditLogger

router = APIRouter()


@router.post(
    "/start",
    response_model=MessageResponse,
    summary="Start analysis",
    description="Start AI analysis with selected prompt"
)
def start_analysis(
    claim_id: int,
    request: AnalyzeRequest,
    db: Session = Depends(get_database),
    audit: AuditLogger = Depends(get_audit_logger),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Start AI analysis with prompt selection.
    """
    from app.worker import analyze_claim_with_rag
    
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    if claim.status != models.ClaimStatus.READY_FOR_ANALYSIS.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Claim is not ready for analysis (current status: {claim.status})"
        )
    
    # Log analysis start
    audit.log(
        user=current_user.id,
        action="ANALYSIS_STARTED",
        entity_type="Claim",
        entity_id=claim_id,
        changes={"prompt_id": request.prompt_id},
        db=db
    )
    
    # Trigger analysis
    analyze_claim_with_rag.delay(claim_id, request.prompt_id, user=current_user.id)
    
    return MessageResponse(
        message=f"Analysis started with prompt '{request.prompt_id}'"
    )


@router.post(
    "/approve",
    response_model=MessageResponse,
    summary="Approve for analysis (legacy)",
    description="Legacy endpoint - approves claim and starts analysis"
)
def approve_claim(
    claim_id: int,
    request: AnalyzeRequest = None,
    db: Session = Depends(get_database),
    audit: AuditLogger = Depends(get_audit_logger),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Legacy approve endpoint - triggers analysis.
    """
    from app.worker import analyze_claim_task
    from app.prompts import get_prompt_template
    
    prompt_id = request.prompt_id if request else "default"
    
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    if claim.status != models.ClaimStatus.WAITING_FOR_APPROVAL.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Claim is not waiting for approval"
        )
    
    # Get prompt template
    prompt_template = get_prompt_template(prompt_id)
    
    # Trigger analysis
    analyze_claim_task.delay(claim.id, prompt_template)
    
    return MessageResponse(message="Claim approved and analysis started")


@router.get(
    "/result",
    summary="Get analysis result",
    description="Get the analysis result for a claim"
)
def get_analysis_result(
    claim_id: int,
    db: Session = Depends(get_database)
):
    """
    Get analysis result for a claim.
    """
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    if not claim.analysis_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis result available"
        )
    
    return {
        "claim_id": claim_id,
        "status": claim.status,
        "model_used": claim.analysis_model,
        "result": claim.analysis_result
    }

