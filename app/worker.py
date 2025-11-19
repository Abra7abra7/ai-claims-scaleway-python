from celery import Celery
from app.core.config import get_settings
from app.db.session import SessionLocal
import app.db.models as models
from app.services.storage import StorageService
from app.services.ocr import OCRService
from app.services.anonymizer import AnonymizerService
from app.services.mistral import MistralService

settings = get_settings()

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

storage_service = StorageService()
ocr_service = OCRService()
anonymizer_service = AnonymizerService()
mistral_service = MistralService()

@celery_app.task(name="app.worker.process_claim")
def process_claim(document_id: int):
    db = SessionLocal()
    try:
        document = db.query(models.ClaimDocument).filter(models.ClaimDocument.id == document_id).first()
        if not document:
            return "Document not found"

        # 1. Download from S3 (Generate Presigned URL for Mistral)
        presigned_url = storage_service.generate_presigned_url(document.s3_key)

        # 2. OCR with Mistral
        ocr_text = ocr_service.extract_text_from_url(presigned_url)
        document.original_text = ocr_text
        
        # 3. Anonymize
        anonymized_text = anonymizer_service.anonymize(ocr_text)
        document.anonymized_text = anonymized_text

        db.commit()
        
        # Check if all documents for this claim are processed
        claim = db.query(models.Claim).filter(models.Claim.id == document.claim_id).first()
        all_docs = db.query(models.ClaimDocument).filter(models.ClaimDocument.claim_id == claim.id).all()
        
        if all(doc.original_text is not None for doc in all_docs):
             claim.status = models.ClaimStatus.WAITING_FOR_APPROVAL.value
             db.commit()

        return f"Document {document_id} processed"
    except Exception as e:
        print(f"Error processing document {document_id}: {e}")
        return f"Error: {e}"
    finally:
        db.close()

@celery_app.task(name="app.worker.analyze_claim_task")
def analyze_claim_task(claim_id: int, custom_prompt: str = None):
    db = SessionLocal()
    try:
        claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
        if not claim:
            return "Claim not found"
            
        # Aggregate text from all documents
        all_docs = db.query(models.ClaimDocument).filter(models.ClaimDocument.claim_id == claim.id).all()
        full_anonymized_text = "\n\n".join([f"Document: {doc.filename}\n{doc.anonymized_text}" for doc in all_docs if doc.anonymized_text])

        # 4. Embeddings (using aggregated text or per document - simplified to aggregated for now)
        # For better RAG, we should embed chunks, but for PoC we embed the full text or just skip embedding the huge blob if not needed for search immediately.
        # Let's generate embedding for the first document as a placeholder or average them.
        # For now, let's just skip saving embedding to claim and focus on analysis.
        
        # 5. RAG & Analysis
        # Simplified RAG: We just pass the text to the LLM
        analysis = mistral_service.analyze_claim(full_anonymized_text, [], custom_prompt)
        
        claim.analysis_result = analysis
        claim.status = models.ClaimStatus.ANALYZED.value
        db.commit()

        return f"Claim {claim_id} analyzed"
    except Exception as e:
        print(f"Error analyzing claim {claim_id}: {e}")
        return f"Error: {e}"
    finally:
        db.close()
