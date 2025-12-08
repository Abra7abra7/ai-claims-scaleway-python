from celery import Celery
from app.core.config import get_settings
from app.core.config_loader import get_config_loader
from app.db.session import SessionLocal
import app.db.models as models
from app.services.storage import StorageService
from app.services.factory import get_llm_service, get_ocr_service
from app.services.cleaner import CleanerService
from app.services.rag import RAGService
from app.services.report_generator import ReportGenerator
from app.services.audit import AuditLogger
from datetime import datetime
import requests

settings = get_settings()
config = get_config_loader()

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Service instances
storage_service = StorageService()
ocr_service = get_ocr_service()      # Using Factory
cleaner_service = CleanerService()
mistral_service = get_llm_service()  # Using Factory (variable name kept for compatibility)
rag_service = RAGService()
report_generator = ReportGenerator()
audit_logger = AuditLogger()

@celery_app.task(name="app.worker.process_claim_ocr")
def process_claim_ocr(document_id: int):
    """
    Step 1: OCR processing
    Extract text from document and set status to OCR_REVIEW
    """
    db = SessionLocal()
    try:
        document = db.query(models.ClaimDocument).filter(
            models.ClaimDocument.id == document_id
        ).first()
        if not document:
            return "Document not found"

        # Download file from S3/MinIO and send as base64
        # This works with local MinIO since we don't need external URL access
        file_bytes = storage_service.download_file_bytes(document.s3_key)
        
        # OCR with Mistral using base64
        ocr_text = ocr_service.extract_text_from_bytes(file_bytes, document.filename)
        document.original_text = ocr_text
        db.commit()
        
        # Check if all documents for this claim have OCR done
        claim = db.query(models.Claim).filter(
            models.Claim.id == document.claim_id
        ).first()
        all_docs = db.query(models.ClaimDocument).filter(
            models.ClaimDocument.claim_id == claim.id
        ).all()
        
        if all(doc.original_text is not None for doc in all_docs):
            # All OCR done, move to OCR_REVIEW status
            claim.status = models.ClaimStatus.OCR_REVIEW.value
            db.commit()

        return f"OCR completed for document {document_id}"
    except Exception as e:
        print(f"Error in OCR processing for document {document_id}: {e}")
        # Mark claim as failed
        try:
            document = db.query(models.ClaimDocument).filter(
                models.ClaimDocument.id == document_id
            ).first()
            if document:
                claim = db.query(models.Claim).filter(
                    models.Claim.id == document.claim_id
                ).first()
                if claim:
                    claim.status = models.ClaimStatus.FAILED.value
                    db.commit()
        except:
            pass
        return f"Error: {e}"
    finally:
        db.close()


@celery_app.task(name="app.worker.clean_document")
def clean_document(document_id: int):
    """
    Step 2: Data cleaning
    Clean OCR text and prepare for anonymization
    """
    db = SessionLocal()
    try:
        document = db.query(models.ClaimDocument).filter(
            models.ClaimDocument.id == document_id
        ).first()
        if not document:
            return "Document not found"
        
        if not document.original_text:
            return "No OCR text to clean"
        
        # Clean text
        cleaned_text = cleaner_service.clean_text(document.original_text)
        document.cleaned_text = cleaned_text
        db.commit()
        
        # Log cleaning completion
        audit_logger.log(
            user="system",
            action=audit_logger.CLEANING_COMPLETED,
            entity_type="ClaimDocument",
            entity_id=document_id,
            db=db
        )
        
        # Check if all documents are cleaned
        claim = db.query(models.Claim).filter(
            models.Claim.id == document.claim_id
        ).first()
        all_docs = db.query(models.ClaimDocument).filter(
            models.ClaimDocument.claim_id == claim.id
        ).all()
        
        if all(doc.cleaned_text is not None for doc in all_docs):
            # All cleaned, trigger anonymization
            claim.status = models.ClaimStatus.ANONYMIZING.value
            db.commit()
            
            # Trigger anonymization tasks
            for doc in all_docs:
                anonymize_document.delay(doc.id, claim.country)
        
        return f"Cleaning completed for document {document_id}"
    except Exception as e:
        print(f"Error cleaning document {document_id}: {e}")
        return f"Error: {e}"
    finally:
        db.close()


@celery_app.task(name="app.worker.anonymize_document")
def anonymize_document(document_id: int, country: str):
    """
    Step 3: Anonymization
    Anonymize text using Presidio API with country-specific recognizers
    """
    db = SessionLocal()
    try:
        document = db.query(models.ClaimDocument).filter(
            models.ClaimDocument.id == document_id
        ).first()
        if not document:
            return "Document not found"
        
        if not document.cleaned_text:
            return "No cleaned text to anonymize"
        
        # Call Presidio API
        presidio_config = config.get_presidio_config()
        presidio_url = presidio_config.get("api_url", "http://presidio:8001")
        
        response = requests.post(
            f"{presidio_url}/anonymize",
            json={
                "text": document.cleaned_text,
                "country": country,
                "language": "en"
            },
            timeout=300  # Extended timeout for large documents
        )
        
        if response.status_code == 200:
            result = response.json()
            document.anonymized_text = result["anonymized_text"]
            db.commit()
        else:
            raise Exception(f"Presidio API error: {response.text}")
        
        # Check if all documents are anonymized
        claim = db.query(models.Claim).filter(
            models.Claim.id == document.claim_id
        ).first()
        all_docs = db.query(models.ClaimDocument).filter(
            models.ClaimDocument.claim_id == claim.id
        ).all()
        
        if all(doc.anonymized_text is not None for doc in all_docs):
            # All anonymized, move to review
            claim.status = models.ClaimStatus.ANONYMIZATION_REVIEW.value
            db.commit()
        
        return f"Anonymization completed for document {document_id}"
    except Exception as e:
        print(f"Error anonymizing document {document_id}: {e}")
        return f"Error: {e}"
    finally:
        db.close()

@celery_app.task(name="app.worker.analyze_claim_with_rag")
def analyze_claim_with_rag(claim_id: int, prompt_id: str, user: str = "admin"):
    """
    Step 4: AI Analysis with RAG
    Analyze claim using RAG context and generate report
    """
    db = SessionLocal()
    try:
        claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
        if not claim:
            return "Claim not found"
        
        # Update status
        claim.status = models.ClaimStatus.ANALYZING.value
        db.commit()
        
        # Determine model used from settings
        model_used = settings.LLM_MODEL_VERSION or f"{settings.LLM_PROVIDER}-default"
        
        # Log analysis start
        audit_logger.log_analysis_started(
            user=user,
            claim_id=claim_id,
            prompt_id=prompt_id,
            model=model_used,
            db=db
        )
        
        # Get RAG context
        context_string, sources = rag_service.get_context_for_claim(claim, db)
        
        # Get prompt template
        prompt_template = config.get_prompt(prompt_id)["template"]
        
        # Aggregate anonymized text
        all_docs = db.query(models.ClaimDocument).filter(
            models.ClaimDocument.claim_id == claim.id
        ).all()
        claim_text = "\n\n".join([
            f"Document: {doc.filename}\n{doc.anonymized_text}"
            for doc in all_docs if doc.anonymized_text
        ])
        
        # Analyze with Selected Provider (mistral_service is now generic LLMProvider)
        analysis = mistral_service.analyze_claim(
            claim_text=claim_text,
            context_documents=[context_string] if context_string else [],
            custom_prompt=prompt_template
        )
        
        # Save analysis result
        claim.analysis_result = analysis
        claim.analysis_model = model_used
        db.commit()
        
        # Log analysis completion
        audit_logger.log_analysis_completed(
            user="system",
            claim_id=claim_id,
            recommendation=analysis.get("recommendation", "N/A"),
            confidence=analysis.get("confidence", 0.0),
            db=db
        )
        
        # Trigger report generation
        generate_report.delay(claim_id, prompt_id, model_used, sources, user)
        
        return f"Analysis completed for claim {claim_id}"
    except Exception as e:
        print(f"Error analyzing claim {claim_id}: {e}")
        # Mark as failed
        try:
            claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
            if claim:
                claim.status = models.ClaimStatus.FAILED.value
                db.commit()
        except:
            pass
        return f"Error: {e}"
    finally:
        db.close()


@celery_app.task(name="app.worker.generate_report")
def generate_report(claim_id: int, prompt_id: str, model_used: str, sources: list = None, user: str = "admin"):
    """
    Step 5: Report Generation
    Generate PDF report and upload to S3
    """
    db = SessionLocal()
    try:
        claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
        if not claim:
            return "Claim not found"
        
        if not claim.analysis_result:
            return "No analysis result to generate report"
        
        # Generate PDF
        pdf_bytes = report_generator.generate_pdf(
            claim=claim,
            analysis_result=claim.analysis_result,
            model_used=model_used,
            prompt_id=prompt_id,
            sources=sources
        )
        
        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        s3_key = f"claims/{claim_id}/reports/analysis_{timestamp}.pdf"
        
        # Upload to S3
        storage_service.upload_bytes(
            file_content=pdf_bytes,
            s3_key=s3_key,
            content_type="application/pdf"
        )
        
        # Save report record
        report = models.AnalysisReport(
            claim_id=claim_id,
            s3_key=s3_key,
            model_used=model_used,
            prompt_id=prompt_id
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        
        # Log report generation
        audit_logger.log_report_generated(
            user=user,
            claim_id=claim_id,
            report_id=report.id,
            db=db
        )
        
        # Update claim status
        claim.status = models.ClaimStatus.ANALYZED.value
        db.commit()
        
        return f"Report generated for claim {claim_id}"
    except Exception as e:
        print(f"Error generating report for claim {claim_id}: {e}")
        return f"Error: {e}"
    finally:
        db.close()


@celery_app.task(name="app.worker.process_rag_document")
def process_rag_document(rag_doc_id: int):
    """
    Process RAG document: extract text and generate embedding
    """
    db = SessionLocal()
    try:
        success = rag_service.process_document(rag_doc_id, db)
        
        if success:
            return f"RAG document {rag_doc_id} processed successfully"
        else:
            return f"Failed to process RAG document {rag_doc_id}"
    except Exception as e:
        print(f"Error processing RAG document {rag_doc_id}: {e}")
        return f"Error: {e}"
    finally:
        db.close()


# Legacy task name for backward compatibility
@celery_app.task(name="app.worker.process_claim")
def process_claim(document_id: int):
    """Legacy task - redirects to new OCR task"""
    return process_claim_ocr(document_id)


@celery_app.task(name="app.worker.analyze_claim_task")
def analyze_claim_task(claim_id: int, custom_prompt: str = None):
    """Legacy task - redirects to new RAG-based analysis"""
    prompt_id = "default" if not custom_prompt else "custom"
    return analyze_claim_with_rag(claim_id, prompt_id)
