"""
RAG (Retrieval-Augmented Generation) management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_database,
    get_audit_logger,
    get_current_user,
    CurrentUser
)
from app.api.v1.schemas.rag import (
    RAGDocumentSummary,
    RAGDocumentListResponse,
    RAGUploadResponse,
    RAGFolderStructure
)
from app.api.v1.schemas.base import MessageResponse, Country, RAGDocumentType
from app.db import models
from app.services.rag import RAGService
from app.services.audit import AuditLogger

router = APIRouter()


@router.get(
    "/documents",
    response_model=list[RAGDocumentSummary],
    summary="List RAG documents",
    description="List all RAG documents with optional filters"
)
def list_rag_documents(
    country: str = Query(None, description="Filter by country"),
    document_type: str = Query(None, description="Filter by document type"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_database)
):
    """
    List RAG documents with optional filters.
    """
    rag_service = RAGService()
    
    docs = rag_service.list_documents(
        db=db,
        country=country,
        document_type=document_type,
        limit=limit,
        offset=offset
    )
    
    return [
        RAGDocumentSummary(
            id=doc.id,
            filename=doc.filename,
            country=doc.country,
            document_type=doc.document_type,
            uploaded_by=doc.uploaded_by,
            created_at=doc.created_at
        )
        for doc in docs
    ]


@router.get(
    "/structure",
    response_model=RAGFolderStructure,
    summary="Get folder structure",
    description="Get hierarchical folder structure of RAG documents"
)
def get_rag_structure(
    db: Session = Depends(get_database)
):
    """
    Get hierarchical folder structure.
    """
    rag_service = RAGService()
    structure = rag_service.get_folder_structure(db)
    
    return RAGFolderStructure(countries=structure)


@router.post(
    "/upload",
    response_model=RAGUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload RAG document",
    description="Upload a new RAG policy document"
)
async def upload_rag_document(
    file: UploadFile = File(..., description="PDF document to upload"),
    country: Country = Query(Country.SK, description="Country code"),
    document_type: RAGDocumentType = Query(RAGDocumentType.GENERAL, description="Document type"),
    db: Session = Depends(get_database),
    audit: AuditLogger = Depends(get_audit_logger),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Upload RAG document and start processing.
    """
    from app.worker import process_rag_document
    
    rag_service = RAGService()
    
    file_content = await file.read()
    
    # Upload document
    rag_doc = rag_service.upload_document(
        file_content=file_content,
        filename=file.filename,
        country=country.value,
        document_type=document_type.value,
        uploaded_by=current_user.id,
        db=db,
        content_type=file.content_type or "application/pdf"
    )
    
    # Log upload
    audit.log_rag_upload(
        user=current_user.id,
        rag_doc_id=rag_doc.id,
        filename=file.filename,
        country=country.value,
        doc_type=document_type.value,
        db=db
    )
    
    # Trigger processing
    process_rag_document.delay(rag_doc.id)
    
    return RAGUploadResponse(
        id=rag_doc.id,
        message="RAG document uploaded and processing started"
    )


@router.get(
    "/documents/{rag_doc_id}",
    response_model=RAGDocumentSummary,
    summary="Get RAG document",
    description="Get details of a specific RAG document"
)
def get_rag_document(
    rag_doc_id: int,
    db: Session = Depends(get_database)
):
    """
    Get RAG document details.
    """
    rag_doc = db.query(models.RAGDocument).filter(
        models.RAGDocument.id == rag_doc_id
    ).first()
    
    if not rag_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RAG document not found"
        )
    
    return RAGDocumentSummary(
        id=rag_doc.id,
        filename=rag_doc.filename,
        country=rag_doc.country,
        document_type=rag_doc.document_type,
        uploaded_by=rag_doc.uploaded_by,
        created_at=rag_doc.created_at
    )


@router.delete(
    "/documents/{rag_doc_id}",
    response_model=MessageResponse,
    summary="Delete RAG document",
    description="Delete a RAG document"
)
def delete_rag_document(
    rag_doc_id: int,
    db: Session = Depends(get_database),
    audit: AuditLogger = Depends(get_audit_logger),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Delete RAG document.
    """
    rag_service = RAGService()
    
    # Get doc for logging
    rag_doc = db.query(models.RAGDocument).filter(
        models.RAGDocument.id == rag_doc_id
    ).first()
    
    if not rag_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RAG document not found"
        )
    
    filename = rag_doc.filename
    
    # Delete
    success = rag_service.delete_document(rag_doc_id, db)
    
    if success:
        # Log deletion
        audit.log_rag_delete(
            user=current_user.id,
            rag_doc_id=rag_doc_id,
            filename=filename,
            db=db
        )
        return MessageResponse(message="RAG document deleted")
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete RAG document"
        )

