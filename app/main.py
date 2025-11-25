from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.config import get_settings
from app.db.session import engine, get_db
from app.db.models import Base, Claim
# from app.worker import process_claim_task # Will implement later

settings = get_settings()

from sqlalchemy import text

# Create tables
with engine.connect() as connection:
    connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    connection.commit()

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

@app.get("/")
def read_root():
    return {"message": "AI Claims Processing API"}

from app.services.storage import StorageService
from app.worker import process_claim
import app.db.models as models

@app.post("/upload/")
async def upload_files(
    files: List[UploadFile] = File(...),
    country: str = "SK",
    db: Session = Depends(get_db)
):
    """
    Upload claim documents with country selection.
    New storage structure: claims/{claim_id}/originals/
    """
    storage_service = StorageService()
    from app.services.audit import AuditLogger
    audit_logger = AuditLogger()
    
    # Create one Claim for the batch with country
    claim = models.Claim(
        status=models.ClaimStatus.PROCESSING.value,
        country=country
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)
    
    # Log claim creation
    audit_logger.log_claim_created(
        user="user",  # TODO: Get from auth
        claim_id=claim.id,
        country=country,
        num_documents=len(files),
        db=db
    )

    for file in files:
        # Upload to S3 with new structure
        try:
            file_content = await file.read()
            s3_key = f"claims/{claim.id}/originals/{file.filename}"
            storage_service.upload_bytes(
                file_content,
                s3_key,
                file.content_type or 'application/pdf'
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Upload failed for {file.filename}: {str(e)}"
            )

        # Create ClaimDocument
        document = models.ClaimDocument(
            claim_id=claim.id,
            filename=file.filename,
            s3_key=s3_key
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        # Trigger OCR processing task for each document
        from app.worker import process_claim_ocr
        process_claim_ocr.delay(document.id)

    return {
        "id": claim.id,
        "country": country,
        "status": "processing",
        "message": f"Created claim {claim.id} with {len(files)} documents"
    }

@app.get("/prompts/")
def get_prompts():
    """Get list of available analysis prompts"""
    from app.prompts import get_prompt_list
    return get_prompt_list()

@app.post("/approve/{claim_id}")
def approve_claim(claim_id: int, request_body: dict = None, db: Session = Depends(get_db)):
    from fastapi import Body
    from app.worker import analyze_claim_task
    from app.prompts import get_prompt_template
    
    # Get prompt_id from request body if provided
    prompt_id = "default"
    if request_body and "prompt_id" in request_body:
        prompt_id = request_body.get("prompt_id")
    
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
        
    if claim.status != models.ClaimStatus.WAITING_FOR_APPROVAL.value:
        raise HTTPException(status_code=400, detail="Claim is not waiting for approval")
    
    # Get the prompt template
    prompt_template = get_prompt_template(prompt_id)
        
    # Trigger Analysis with selected prompt
    analyze_claim_task.delay(claim.id, prompt_template)
    
    return {"message": "Claim approved and analysis started"}

@app.get("/claims/")
def list_claims(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    claims = db.query(models.Claim).offset(skip).limit(limit).all()
    result = []
    for claim in claims:
        claim_dict = {
            "id": claim.id,
            "created_at": claim.created_at.isoformat() if claim.created_at else None,
            "country": claim.country if claim.country else "Unknown",
            "status": claim.status,
            "analysis_result": claim.analysis_result,
            "documents": [
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "s3_key": doc.s3_key,
                    "original_text": doc.original_text,
                    "anonymized_text": doc.anonymized_text
                }
                for doc in claim.documents
            ]
        }
        result.append(claim_dict)
    return result

@app.get("/claims/{claim_id}")
def get_claim(claim_id: int, db: Session = Depends(get_db)):
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    return {
        "id": claim.id,
        "created_at": claim.created_at.isoformat() if claim.created_at else None,
        "country": claim.country,
        "status": claim.status,
        "analysis_result": claim.analysis_result,
        "analysis_model": claim.analysis_model,
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "s3_key": doc.s3_key,
                "original_text": doc.original_text,
                "cleaned_text": doc.cleaned_text,
                "anonymized_text": doc.anonymized_text,
                "ocr_reviewed_by": doc.ocr_reviewed_by,
                "ocr_reviewed_at": doc.ocr_reviewed_at.isoformat() if doc.ocr_reviewed_at else None,
                "anon_reviewed_by": doc.anon_reviewed_by,
                "anon_reviewed_at": doc.anon_reviewed_at.isoformat() if doc.anon_reviewed_at else None
            }
            for doc in claim.documents
        ]
    }


# ==================== HITL: OCR Review Endpoints ====================

@app.get("/claims/{claim_id}/ocr-review")
def get_ocr_review(claim_id: int, db: Session = Depends(get_db)):
    """Get claim for OCR review"""
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    if claim.status != models.ClaimStatus.OCR_REVIEW.value:
        raise HTTPException(
            status_code=400,
            detail=f"Claim is not in OCR_REVIEW status (current: {claim.status})"
        )
    
    return {
        "claim_id": claim.id,
        "country": claim.country,
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "original_text": doc.original_text
            }
            for doc in claim.documents
        ]
    }


@app.post("/claims/{claim_id}/ocr-edit")
def edit_ocr(claim_id: int, edits: dict, db: Session = Depends(get_db)):
    """
    Edit OCR text for documents.
    Body: {"document_id": new_text, ...}
    """
    from app.services.audit import AuditLogger
    audit_logger = AuditLogger()
    
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    for doc_id_str, new_text in edits.items():
        doc_id = int(doc_id_str)
        document = db.query(models.ClaimDocument).filter(
            models.ClaimDocument.id == doc_id,
            models.ClaimDocument.claim_id == claim_id
        ).first()
        
        if document:
            old_text = document.original_text
            document.original_text = new_text
            document.ocr_reviewed_by = "admin"  # TODO: Get from auth
            document.ocr_reviewed_at = models.datetime.utcnow()
            
            # Log edit
            audit_logger.log_ocr_edit(
                user="admin",
                document_id=doc_id,
                old_text=old_text or "",
                new_text=new_text,
                db=db
            )
    
    db.commit()
    return {"message": "OCR text updated"}


@app.post("/claims/{claim_id}/ocr-approve")
def approve_ocr(claim_id: int, db: Session = Depends(get_db)):
    """Approve OCR and trigger cleaning"""
    from app.services.audit import AuditLogger
    from app.worker import clean_document
    audit_logger = AuditLogger()
    
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    if claim.status != models.ClaimStatus.OCR_REVIEW.value:
        raise HTTPException(status_code=400, detail="Claim is not in OCR_REVIEW status")
    
    # Mark documents as reviewed
    for doc in claim.documents:
        if not doc.ocr_reviewed_by:
            doc.ocr_reviewed_by = "admin"
            doc.ocr_reviewed_at = models.datetime.utcnow()
        
        # Log approval
        audit_logger.log_ocr_approval(
            user="admin",
            document_id=doc.id,
            db=db
        )
    
    # Update status
    claim.status = models.ClaimStatus.CLEANING.value
    db.commit()
    
    # Trigger cleaning tasks
    for doc in claim.documents:
        clean_document.delay(doc.id)
    
    return {"message": "OCR approved, cleaning started"}


# ==================== HITL: Anonymization Review Endpoints ====================

@app.get("/claims/{claim_id}/anon-review")
def get_anon_review(claim_id: int, db: Session = Depends(get_db)):
    """Get claim for anonymization review"""
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    if claim.status != models.ClaimStatus.ANONYMIZATION_REVIEW.value:
        raise HTTPException(
            status_code=400,
            detail=f"Claim is not in ANONYMIZATION_REVIEW status (current: {claim.status})"
        )
    
    return {
        "claim_id": claim.id,
        "country": claim.country,
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "cleaned_text": doc.cleaned_text,
                "anonymized_text": doc.anonymized_text
            }
            for doc in claim.documents
        ]
    }


@app.post("/claims/{claim_id}/anon-edit")
def edit_anon(claim_id: int, edits: dict, db: Session = Depends(get_db)):
    """
    Edit anonymized text for documents.
    Body: {"document_id": new_anonymized_text, ...}
    """
    from app.services.audit import AuditLogger
    audit_logger = AuditLogger()
    
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    for doc_id_str, new_text in edits.items():
        doc_id = int(doc_id_str)
        document = db.query(models.ClaimDocument).filter(
            models.ClaimDocument.id == doc_id,
            models.ClaimDocument.claim_id == claim_id
        ).first()
        
        if document:
            old_text = document.anonymized_text
            document.anonymized_text = new_text
            document.anon_reviewed_by = "admin"
            document.anon_reviewed_at = models.datetime.utcnow()
            
            # Log edit
            audit_logger.log_anon_edit(
                user="admin",
                document_id=doc_id,
                old_text=old_text or "",
                new_text=new_text,
                db=db
            )
    
    db.commit()
    return {"message": "Anonymized text updated"}


@app.post("/claims/{claim_id}/anon-approve")
def approve_anon(claim_id: int, db: Session = Depends(get_db)):
    """Approve anonymization and set ready for analysis"""
    from app.services.audit import AuditLogger
    audit_logger = AuditLogger()
    
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    if claim.status != models.ClaimStatus.ANONYMIZATION_REVIEW.value:
        raise HTTPException(
            status_code=400,
            detail="Claim is not in ANONYMIZATION_REVIEW status"
        )
    
    # Mark documents as reviewed
    for doc in claim.documents:
        if not doc.anon_reviewed_by:
            doc.anon_reviewed_by = "admin"
            doc.anon_reviewed_at = models.datetime.utcnow()
    
    # Log approval
    audit_logger.log_anon_approval(
        user="admin",
        claim_id=claim.id,
        db=db
    )
    
    # Update status
    claim.status = models.ClaimStatus.READY_FOR_ANALYSIS.value
    db.commit()
    
    return {"message": "Anonymization approved, ready for analysis"}


@app.post("/claims/{claim_id}/retry-anonymization")
def retry_anonymization(claim_id: int, db: Session = Depends(get_db)):
    """
    Retry anonymization for claims stuck in ANONYMIZING state.
    Useful when Presidio was down or anonymization failed.
    """
    from app.worker import anonymize_document, clean_document
    from app.services.audit import AuditLogger
    
    audit_logger = AuditLogger()
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    if claim.status not in [models.ClaimStatus.ANONYMIZING.value, models.ClaimStatus.CLEANING.value]:
        raise HTTPException(
            status_code=400, 
            detail=f"Claim is in {claim.status} status. Retry only works for ANONYMIZING or CLEANING status."
        )
    
    # Count documents that need re-processing
    docs_to_retry = []
    for doc in claim.documents:
        if claim.status == models.ClaimStatus.ANONYMIZING.value:
            if doc.cleaned_text and not doc.anonymized_text:
                docs_to_retry.append(doc)
        elif claim.status == models.ClaimStatus.CLEANING.value:
            if doc.original_text and not doc.cleaned_text:
                docs_to_retry.append(doc)
    
    if not docs_to_retry:
        return {"message": "No documents need retry", "count": 0}
    
    # Trigger tasks
    if claim.status == models.ClaimStatus.ANONYMIZING.value:
        for doc in docs_to_retry:
            anonymize_document.delay(doc.id, claim.country)
            audit_logger.log(
                user="admin",
                action="ANONYMIZATION_RETRY",
                entity_type="ClaimDocument",
                entity_id=doc.id,
                db=db
            )
    elif claim.status == models.ClaimStatus.CLEANING.value:
        for doc in docs_to_retry:
            clean_document.delay(doc.id)
            audit_logger.log(
                user="admin",
                action="CLEANING_RETRY",
                entity_type="ClaimDocument",
                entity_id=doc.id,
                db=db
            )
    
    return {
        "message": f"Retry triggered for {len(docs_to_retry)} documents",
        "count": len(docs_to_retry),
        "claim_id": claim_id,
        "status": claim.status
    }


@app.post("/claims/{claim_id}/reset-status")
def reset_claim_status(claim_id: int, db: Session = Depends(get_db)):
    """
    Manually reset claim status from ANALYZING/FAILED to READY_FOR_ANALYSIS.
    Useful when analysis task gets stuck or fails.
    """
    from app.services.audit import AuditLogger
    audit_logger = AuditLogger()
    
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
        
    # Allow reset from ANALYZING, FAILED, or even ANALYZED if re-run is needed
    if claim.status not in [models.ClaimStatus.ANALYZING.value, models.ClaimStatus.FAILED.value, models.ClaimStatus.ANALYZED.value]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot reset status from {claim.status}. Only allowed from ANALYZING, FAILED or ANALYZED."
        )
    
    old_status = claim.status
    claim.status = models.ClaimStatus.READY_FOR_ANALYSIS.value
    db.commit()
    
    audit_logger.log(
        user="admin",
        action="STATUS_RESET",
        entity_type="Claim",
        entity_id=claim_id,
        changes={"from": old_status, "to": claim.status},
        db=db
    )
    
    return {"message": f"Claim status reset from {old_status} to {claim.status}"}


# ==================== Analysis with Prompts ====================

@app.get("/prompts-config/")
def get_prompts_config():
    """Get list of available analysis prompts from config"""
    from app.core.config_loader import get_config_loader
    config = get_config_loader()
    return config.get_prompt_list()


@app.post("/analyze/{claim_id}")
def analyze_claim_endpoint(claim_id: int, request_body: dict, db: Session = Depends(get_db)):
    """
    Start analysis with prompt selection.
    Body: {"prompt_id": "default|fraud_detection|..."}
    """
    from app.worker import analyze_claim_with_rag
    
    prompt_id = request_body.get("prompt_id", "default")
    
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    if claim.status != models.ClaimStatus.READY_FOR_ANALYSIS.value:
        raise HTTPException(
            status_code=400,
            detail=f"Claim is not ready for analysis (current status: {claim.status})"
        )
    
    # Trigger analysis
    analyze_claim_with_rag.delay(claim_id, prompt_id, user="admin")
    
    return {"message": "Analysis started", "prompt_id": prompt_id}


# ==================== RAG Management Endpoints ====================

@app.get("/rag/documents")
def list_rag_documents(
    country: str = None,
    document_type: str = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List RAG documents with optional filters"""
    from app.services.rag import RAGService
    rag_service = RAGService()
    
    docs = rag_service.list_documents(
        db=db,
        country=country,
        document_type=document_type,
        limit=limit,
        offset=offset
    )
    
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "country": doc.country,
            "document_type": doc.document_type,
            "uploaded_by": doc.uploaded_by,
            "created_at": doc.created_at.isoformat() if doc.created_at else None
        }
        for doc in docs
    ]


@app.get("/rag/structure")
def get_rag_structure(db: Session = Depends(get_db)):
    """Get hierarchical folder structure"""
    from app.services.rag import RAGService
    rag_service = RAGService()
    return rag_service.get_folder_structure(db)


@app.post("/rag/upload")
async def upload_rag_document(
    file: UploadFile = File(...),
    country: str = "SK",
    document_type: str = "general",
    db: Session = Depends(get_db)
):
    """Upload RAG document"""
    from app.services.rag import RAGService
    from app.services.audit import AuditLogger
    from app.worker import process_rag_document
    
    rag_service = RAGService()
    audit_logger = AuditLogger()
    
    file_content = await file.read()
    
    # Upload document
    rag_doc = rag_service.upload_document(
        file_content=file_content,
        filename=file.filename,
        country=country,
        document_type=document_type,
        uploaded_by="admin",  # TODO: Get from auth
        db=db,
        content_type=file.content_type or "application/pdf"
    )
    
    # Log upload
    audit_logger.log_rag_upload(
        user="admin",
        rag_doc_id=rag_doc.id,
        filename=file.filename,
        country=country,
        doc_type=document_type,
        db=db
    )
    
    # Trigger processing (OCR + embedding)
    process_rag_document.delay(rag_doc.id)
    
    return {
        "id": rag_doc.id,
        "message": "RAG document uploaded and processing started"
    }


@app.delete("/rag/documents/{rag_doc_id}")
def delete_rag_document(rag_doc_id: int, db: Session = Depends(get_db)):
    """Delete RAG document"""
    from app.services.rag import RAGService
    from app.services.audit import AuditLogger
    
    rag_service = RAGService()
    audit_logger = AuditLogger()
    
    # Get doc for logging
    rag_doc = db.query(models.RAGDocument).filter(
        models.RAGDocument.id == rag_doc_id
    ).first()
    
    if not rag_doc:
        raise HTTPException(status_code=404, detail="RAG document not found")
    
    filename = rag_doc.filename
    
    # Delete
    success = rag_service.delete_document(rag_doc_id, db)
    
    if success:
        # Log deletion
        audit_logger.log_rag_delete(
            user="admin",
            rag_doc_id=rag_doc_id,
            filename=filename,
            db=db
        )
        return {"message": "RAG document deleted"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete RAG document")


# ==================== Reports Endpoints ====================

@app.get("/claims/{claim_id}/reports")
def get_claim_reports(claim_id: int, db: Session = Depends(get_db)):
    """Get all reports for a claim"""
    reports = db.query(models.AnalysisReport).filter(
        models.AnalysisReport.claim_id == claim_id
    ).order_by(models.AnalysisReport.created_at.desc()).all()
    
    return [
        {
            "id": report.id,
            "s3_key": report.s3_key,
            "model_used": report.model_used,
            "prompt_id": report.prompt_id,
            "created_at": report.created_at.isoformat() if report.created_at else None
        }
        for report in reports
    ]


@app.get("/reports/{report_id}/download")
def download_report(report_id: int, db: Session = Depends(get_db)):
    """Get presigned URL for report download"""
    report = db.query(models.AnalysisReport).filter(
        models.AnalysisReport.id == report_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    storage_service = StorageService()
    presigned_url = storage_service.generate_presigned_url(report.s3_key)
    
    return {"download_url": presigned_url}


# ==================== Audit Logs Endpoints ====================

@app.get("/audit-logs")
def get_audit_logs(
    entity_type: str = None,
    entity_id: int = None,
    user: str = None,
    action: str = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get audit logs with filters"""
    from app.services.audit import AuditLogger
    audit_logger = AuditLogger()
    
    logs = audit_logger.get_logs(
        db=db,
        entity_type=entity_type,
        entity_id=entity_id,
        user=user,
        action=action,
        limit=limit,
        offset=offset
    )
    
    return [
        {
            "id": log.id,
            "user": log.user,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "changes": log.changes,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None
        }
        for log in logs
    ]


@app.get("/claims/{claim_id}/audit-trail")
def get_claim_audit_trail(claim_id: int, db: Session = Depends(get_db)):
    """Get complete audit trail for a claim"""
    from app.services.audit import AuditLogger
    audit_logger = AuditLogger()
    
    return audit_logger.get_claim_audit_trail(claim_id, db)

