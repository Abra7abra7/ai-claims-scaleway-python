"""
Claims CRUD endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import (
    get_database,
    get_audit_logger,
    get_storage_service,
    get_current_user,
    CurrentUser,
    PaginationParams,
    get_pagination
)
from app.api.v1.schemas.claims import (
    ClaimListResponse,
    ClaimDetail,
    ClaimSummary,
    ClaimUploadResponse,
    ClaimUpdateRequest
)
from app.api.v1.schemas.base import MessageResponse, Country, ClaimStatus
from app.db import models
from app.services.storage import StorageService
from app.services.audit import AuditLogger

router = APIRouter()


@router.get(
    "",
    response_model=ClaimListResponse,
    summary="List all claims",
    description="Get paginated list of all claims with optional filters"
)
def list_claims(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Max records to return"),
    status_filter: str = Query(None, alias="status", description="Filter by status"),
    country: str = Query(None, description="Filter by country"),
    db: Session = Depends(get_database)
):
    """
    List all claims with pagination and optional filters.
    """
    query = db.query(models.Claim)
    
    if status_filter:
        query = query.filter(models.Claim.status == status_filter)
    if country:
        query = query.filter(models.Claim.country == country)
    
    total = query.count()
    claims = query.order_by(models.Claim.created_at.desc()).offset(skip).limit(limit).all()
    
    items = []
    for claim in claims:
        items.append(ClaimSummary(
            id=claim.id,
            country=claim.country or "Unknown",
            status=claim.status,
            created_at=claim.created_at,
            document_count=len(claim.documents)
        ))
    
    return ClaimListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{claim_id}",
    response_model=ClaimDetail,
    summary="Get claim details",
    responses={404: {"description": "Claim not found"}}
)
def get_claim(
    claim_id: int,
    db: Session = Depends(get_database)
):
    """
    Get detailed information about a specific claim.
    """
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    return ClaimDetail(
        id=claim.id,
        country=claim.country,
        status=claim.status,
        created_at=claim.created_at,
        analysis_result=claim.analysis_result,
        analysis_model=claim.analysis_model,
        documents=[
            {
                "id": doc.id,
                "filename": doc.filename,
                "s3_key": doc.s3_key,
                "original_text": doc.original_text,
                "cleaned_text": doc.cleaned_text,
                "anonymized_text": doc.anonymized_text,
                "ocr_reviewed_by": doc.ocr_reviewed_by,
                "ocr_reviewed_at": doc.ocr_reviewed_at,
                "anon_reviewed_by": doc.anon_reviewed_by,
                "anon_reviewed_at": doc.anon_reviewed_at
            }
            for doc in claim.documents
        ]
    )


@router.post(
    "/upload",
    response_model=ClaimUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload new claim documents",
    description="Upload one or more PDF documents to create a new claim"
)
async def upload_claim(
    files: List[UploadFile] = File(..., description="PDF documents to upload"),
    country: Country = Query(Country.SK, description="Country code"),
    contract_number: Optional[str] = Query(None, description="Contract number for legacy system integration"),
    db: Session = Depends(get_database),
    storage: StorageService = Depends(get_storage_service),
    audit: AuditLogger = Depends(get_audit_logger),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Upload claim documents and start OCR processing.
    """
    # Create claim
    claim = models.Claim(
        status=models.ClaimStatus.PROCESSING.value,
        country=country.value,
        contract_number=contract_number
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)
    
    # Log claim creation
    audit.log_claim_created(
        user=current_user.id,
        claim_id=claim.id,
        country=country.value,
        num_documents=len(files),
        db=db
    )
    
    # Upload files
    for file in files:
        try:
            file_content = await file.read()
            s3_key = f"claims/{claim.id}/originals/{file.filename}"
            storage.upload_bytes(
                file_content,
                s3_key,
                file.content_type or 'application/pdf'
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Upload failed for {file.filename}: {str(e)}"
            )
        
        # Create document record
        document = models.ClaimDocument(
            claim_id=claim.id,
            filename=file.filename,
            s3_key=s3_key
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Trigger OCR processing
        from app.worker import process_claim_ocr
        process_claim_ocr.delay(document.id)
    
    return ClaimUploadResponse(
        id=claim.id,
        country=country.value,
        status="processing",
        message=f"Created claim {claim.id} with {len(files)} documents",
        document_count=len(files)
    )


@router.patch(
    "/{claim_id}",
    response_model=ClaimDetail,
    summary="Update claim metadata",
    responses={404: {"description": "Claim not found"}}
)
def update_claim(
    claim_id: int,
    update_data: ClaimUpdateRequest,
    db: Session = Depends(get_database),
    audit: AuditLogger = Depends(get_audit_logger),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Update claim metadata (country, status).
    """
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    old_status = claim.status
    
    if update_data.country:
        claim.country = update_data.country.value
    if update_data.status:
        claim.status = update_data.status.value
    
    db.commit()
    db.refresh(claim)
    
    # Log status change
    if update_data.status and old_status != claim.status:
        audit.log_status_change(
            user=current_user.id,
            claim_id=claim_id,
            old_status=old_status,
            new_status=claim.status,
            db=db
        )
    
    return get_claim(claim_id, db)


@router.delete(
    "/{claim_id}",
    response_model=MessageResponse,
    summary="Delete a claim",
    responses={404: {"description": "Claim not found"}}
)
def delete_claim(
    claim_id: int,
    db: Session = Depends(get_database),
    storage: StorageService = Depends(get_storage_service),
    audit: AuditLogger = Depends(get_audit_logger),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Delete a claim and all associated documents.
    """
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    # Delete from S3
    for doc in claim.documents:
        try:
            storage.s3_client.delete_object(
                Bucket=storage.bucket_name,
                Key=doc.s3_key
            )
        except Exception:
            pass  # Continue even if S3 delete fails
    
    # Log deletion
    audit.log(
        user=current_user.id,
        action="CLAIM_DELETED",
        entity_type="Claim",
        entity_id=claim_id,
        changes={"country": claim.country, "status": claim.status},
        db=db
    )
    
    # Delete from database
    db.delete(claim)
    db.commit()
    
    return MessageResponse(message=f"Claim {claim_id} deleted successfully")

