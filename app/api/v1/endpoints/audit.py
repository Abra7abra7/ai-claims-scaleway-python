"""
Audit log endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_database,
    get_audit_logger,
    require_admin,
    CurrentUser
)
from app.api.v1.schemas.audit import (
    AuditLogDetail,
    AuditLogListResponse,
    ClaimAuditTrail
)
from app.services.audit import AuditLogger

router = APIRouter()


@router.get(
    "/logs",
    response_model=AuditLogListResponse,
    summary="Get audit logs",
    description="Get audit logs with optional filters"
)
def get_audit_logs(
    entity_type: str = Query(None, description="Filter by entity type"),
    entity_id: int = Query(None, description="Filter by entity ID"),
    user: str = Query(None, description="Filter by username"),
    action: str = Query(None, description="Filter by action type"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_database),
    audit: AuditLogger = Depends(get_audit_logger),
    current_user: CurrentUser = Depends(require_admin)
):
    """
    Get audit logs with filters.
    Admin only.
    """
    logs = audit.get_logs(
        db=db,
        entity_type=entity_type,
        entity_id=entity_id,
        user=user,
        action=action,
        limit=limit,
        offset=offset
    )
    
    return AuditLogListResponse(
        items=[
            AuditLogDetail(
                id=log.id,
                user=log.user,
                action=log.action,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                changes=log.changes,
                timestamp=log.timestamp
            )
            for log in logs
        ],
        total=len(logs),  # Note: This is not the total count, just current page
        skip=offset,
        limit=limit
    )


@router.get(
    "/claims/{claim_id}",
    response_model=ClaimAuditTrail,
    summary="Get claim audit trail",
    description="Get complete audit trail for a specific claim"
)
def get_claim_audit_trail(
    claim_id: int,
    db: Session = Depends(get_database),
    audit: AuditLogger = Depends(get_audit_logger)
):
    """
    Get complete audit trail for a claim.
    """
    trail = audit.get_claim_audit_trail(claim_id, db)
    
    if not trail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found or no audit trail available"
        )
    
    return ClaimAuditTrail(
        claim_id=claim_id,
        events=[
            AuditLogDetail(
                id=event["id"],
                user=event["user"],
                action=event["action"],
                entity_type=event["entity_type"],
                entity_id=event["entity_id"],
                changes=event.get("changes"),
                timestamp=event.get("timestamp")
            )
            for event in trail
        ],
        total_events=len(trail)
    )


@router.get(
    "/actions",
    summary="Get available actions",
    description="Get list of available audit action types"
)
def get_audit_actions():
    """
    Get list of available audit action types.
    """
    return {
        "actions": [
            "OCR_EDITED",
            "OCR_APPROVED",
            "CLEANING_COMPLETED",
            "ANON_EDITED",
            "ANON_APPROVED",
            "CLAIM_CREATED",
            "CLAIM_DELETED",
            "CLAIM_STATUS_CHANGED",
            "ANALYSIS_STARTED",
            "ANALYSIS_COMPLETED",
            "REPORT_GENERATED",
            "RAG_DOCUMENT_UPLOADED",
            "RAG_DOCUMENT_DELETED",
            "RE_CLEAN",
            "ANONYMIZATION_RETRY",
            "CLEANING_RETRY",
            "STATUS_RESET"
        ]
    }

