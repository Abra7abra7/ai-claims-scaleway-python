"""
Document download endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from app.api.deps import get_database, get_storage_service
from app.api.v1.schemas.base import MessageResponse
from app.db import models
from app.services.storage import StorageService

router = APIRouter()


@router.get(
    "/{document_id}/download",
    summary="Download document",
    description="Stream document file directly from storage"
)
def download_document(
    document_id: int,
    db: Session = Depends(get_database),
    storage: StorageService = Depends(get_storage_service)
):
    """
    Stream document file directly from MinIO to browser.
    """
    document = db.query(models.ClaimDocument).filter(
        models.ClaimDocument.id == document_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if not document.s3_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found in storage"
        )
    
    try:
        # Download file from MinIO
        file_content = storage.download_bytes(document.s3_key)
        
        # Stream to browser
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="{document.filename}"',
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "public, max-age=3600"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document: {str(e)}"
        )

