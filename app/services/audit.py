from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, Optional, List
import app.db.models as models
import json


class AuditLogger:
    """
    Audit logging service for compliance and tracking.
    Logs all important actions and changes in the system.
    """
    
    # Action types
    OCR_EDITED = "OCR_EDITED"
    OCR_APPROVED = "OCR_APPROVED"
    CLEANING_COMPLETED = "CLEANING_COMPLETED"
    ANON_EDITED = "ANON_EDITED"
    ANON_APPROVED = "ANON_APPROVED"
    CLAIM_CREATED = "CLAIM_CREATED"
    CLAIM_STATUS_CHANGED = "CLAIM_STATUS_CHANGED"
    ANALYSIS_STARTED = "ANALYSIS_STARTED"
    ANALYSIS_COMPLETED = "ANALYSIS_COMPLETED"
    REPORT_GENERATED = "REPORT_GENERATED"
    RAG_DOCUMENT_UPLOADED = "RAG_DOCUMENT_UPLOADED"
    RAG_DOCUMENT_DELETED = "RAG_DOCUMENT_DELETED"
    
    def __init__(self):
        pass
    
    def log(
        self,
        user: str,
        action: str,
        entity_type: str,
        entity_id: int,
        changes: Optional[Dict[str, Any]] = None,
        db: Session = None
    ) -> Optional[models.AuditLog]:
        """
        Log an action to the audit log.
        
        Args:
            user: Username of the person performing the action
            action: Action type (use class constants)
            entity_type: Type of entity (Claim, ClaimDocument, RAGDocument, etc.)
            entity_id: ID of the entity
            changes: Optional dictionary of changes (old_value, new_value)
            db: Database session
            
        Returns:
            Created AuditLog instance or None if db not provided
        """
        if db is None:
            # If no DB session, just print (for debugging)
            print(f"[AUDIT] {user} | {action} | {entity_type}:{entity_id}")
            if changes:
                print(f"  Changes: {json.dumps(changes, indent=2)}")
            return None
        
        audit_log = models.AuditLog(
            user=user,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes,
            timestamp=datetime.utcnow()
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log
    
    def log_ocr_edit(
        self,
        user: str,
        document_id: int,
        old_text: str,
        new_text: str,
        db: Session
    ):
        """Log OCR text edit"""
        changes = {
            "old_value": old_text[:500] if old_text else "",  # Truncate for storage
            "new_value": new_text[:500] if new_text else "",
            "changed_length": len(new_text) - len(old_text) if old_text and new_text else 0
        }
        
        return self.log(
            user=user,
            action=self.OCR_EDITED,
            entity_type="ClaimDocument",
            entity_id=document_id,
            changes=changes,
            db=db
        )
    
    def log_ocr_approval(
        self,
        user: str,
        document_id: int,
        db: Session
    ):
        """Log OCR approval"""
        return self.log(
            user=user,
            action=self.OCR_APPROVED,
            entity_type="ClaimDocument",
            entity_id=document_id,
            db=db
        )
    
    def log_anon_edit(
        self,
        user: str,
        document_id: int,
        old_text: str,
        new_text: str,
        db: Session
    ):
        """Log anonymization text edit"""
        changes = {
            "old_value": old_text[:500] if old_text else "",
            "new_value": new_text[:500] if new_text else "",
            "changed_length": len(new_text) - len(old_text) if old_text and new_text else 0
        }
        
        return self.log(
            user=user,
            action=self.ANON_EDITED,
            entity_type="ClaimDocument",
            entity_id=document_id,
            changes=changes,
            db=db
        )
    
    def log_anon_approval(
        self,
        user: str,
        claim_id: int,
        db: Session
    ):
        """Log anonymization approval"""
        return self.log(
            user=user,
            action=self.ANON_APPROVED,
            entity_type="Claim",
            entity_id=claim_id,
            db=db
        )
    
    def log_claim_created(
        self,
        user: str,
        claim_id: int,
        country: str,
        num_documents: int,
        db: Session
    ):
        """Log claim creation"""
        changes = {
            "country": country,
            "num_documents": num_documents
        }
        
        return self.log(
            user=user,
            action=self.CLAIM_CREATED,
            entity_type="Claim",
            entity_id=claim_id,
            changes=changes,
            db=db
        )
    
    def log_status_change(
        self,
        user: str,
        claim_id: int,
        old_status: str,
        new_status: str,
        db: Session
    ):
        """Log claim status change"""
        changes = {
            "old_value": old_status,
            "new_value": new_status
        }
        
        return self.log(
            user=user,
            action=self.CLAIM_STATUS_CHANGED,
            entity_type="Claim",
            entity_id=claim_id,
            changes=changes,
            db=db
        )
    
    def log_analysis_started(
        self,
        user: str,
        claim_id: int,
        prompt_id: str,
        model: str,
        db: Session
    ):
        """Log analysis start"""
        changes = {
            "prompt_id": prompt_id,
            "model": model
        }
        
        return self.log(
            user=user,
            action=self.ANALYSIS_STARTED,
            entity_type="Claim",
            entity_id=claim_id,
            changes=changes,
            db=db
        )
    
    def log_analysis_completed(
        self,
        user: str,
        claim_id: int,
        recommendation: str,
        confidence: float,
        db: Session
    ):
        """Log analysis completion"""
        changes = {
            "recommendation": recommendation,
            "confidence": confidence
        }
        
        return self.log(
            user=user,
            action=self.ANALYSIS_COMPLETED,
            entity_type="Claim",
            entity_id=claim_id,
            changes=changes,
            db=db
        )
    
    def log_report_generated(
        self,
        user: str,
        claim_id: int,
        report_id: int,
        db: Session
    ):
        """Log report generation"""
        changes = {
            "report_id": report_id
        }
        
        return self.log(
            user=user,
            action=self.REPORT_GENERATED,
            entity_type="Claim",
            entity_id=claim_id,
            changes=changes,
            db=db
        )
    
    def log_rag_upload(
        self,
        user: str,
        rag_doc_id: int,
        filename: str,
        country: str,
        doc_type: str,
        db: Session
    ):
        """Log RAG document upload"""
        changes = {
            "filename": filename,
            "country": country,
            "document_type": doc_type
        }
        
        return self.log(
            user=user,
            action=self.RAG_DOCUMENT_UPLOADED,
            entity_type="RAGDocument",
            entity_id=rag_doc_id,
            changes=changes,
            db=db
        )
    
    def log_rag_delete(
        self,
        user: str,
        rag_doc_id: int,
        filename: str,
        db: Session
    ):
        """Log RAG document deletion"""
        changes = {
            "filename": filename
        }
        
        return self.log(
            user=user,
            action=self.RAG_DOCUMENT_DELETED,
            entity_type="RAGDocument",
            entity_id=rag_doc_id,
            changes=changes,
            db=db
        )
    
    def get_logs(
        self,
        db: Session,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        user: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[models.AuditLog]:
        """
        Retrieve audit logs with filters.
        
        Args:
            db: Database session
            entity_type: Optional entity type filter
            entity_id: Optional entity ID filter
            user: Optional user filter
            action: Optional action filter
            limit: Maximum number of results
            offset: Result offset for pagination
            
        Returns:
            List of AuditLog instances
        """
        query = db.query(models.AuditLog)
        
        if entity_type:
            query = query.filter(models.AuditLog.entity_type == entity_type)
        
        if entity_id is not None:
            query = query.filter(models.AuditLog.entity_id == entity_id)
        
        if user:
            query = query.filter(models.AuditLog.user == user)
        
        if action:
            query = query.filter(models.AuditLog.action == action)
        
        query = query.order_by(models.AuditLog.timestamp.desc())
        query = query.limit(limit).offset(offset)
        
        return query.all()
    
    def get_claim_audit_trail(
        self,
        claim_id: int,
        db: Session
    ) -> List[Dict[str, Any]]:
        """
        Get complete audit trail for a claim including all related documents.
        
        Args:
            claim_id: Claim ID
            db: Database session
            
        Returns:
            List of audit log dictionaries
        """
        # Get claim logs
        claim_logs = self.get_logs(
            db=db,
            entity_type="Claim",
            entity_id=claim_id,
            limit=1000
        )
        
        # Get document logs for this claim
        claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
        if not claim:
            return []
        
        document_logs = []
        for doc in claim.documents:
            doc_logs = self.get_logs(
                db=db,
                entity_type="ClaimDocument",
                entity_id=doc.id,
                limit=1000
            )
            document_logs.extend(doc_logs)
        
        # Combine and sort by timestamp
        all_logs = claim_logs + document_logs
        all_logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Format as dictionaries
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
            for log in all_logs
        ]

