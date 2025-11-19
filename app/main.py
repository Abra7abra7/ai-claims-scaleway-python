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
async def upload_files(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    storage_service = StorageService()
    
    # Create one Claim for the batch
    claim = models.Claim(status=models.ClaimStatus.PROCESSING.value)
    db.add(claim)
    db.commit()
    db.refresh(claim)

    for file in files:
        # Upload to S3
        try:
            file_content = await file.read()
            s3_key = f"claims/{claim.id}/{file.filename}"
            storage_service.upload_bytes(file_content, s3_key, file.content_type or 'application/pdf')
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed for {file.filename}: {str(e)}")

        # Create ClaimDocument
        document = models.ClaimDocument(
            claim_id=claim.id,
            filename=file.filename,
            s3_key=s3_key
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        # Trigger processing task for each document
        process_claim.delay(document.id)

    return {"id": claim.id, "status": "processing", "message": f"Created claim {claim.id} with {len(files)} documents"}

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

