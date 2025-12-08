from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
import app.db.models as models
from app.services.storage import StorageService
from app.services.factory import get_ocr_service, get_llm_service
from app.core.config_loader import get_config_loader
import os


class RAGService:
    """
    RAG (Retrieval-Augmented Generation) Service.
    Manages policy documents for context retrieval.
    """
    
    def __init__(self):
        self.storage_service = StorageService()
        self.ocr_service = get_ocr_service()
        self.mistral_service = get_llm_service() # Keeps variable name for compatibility but uses factory
        self.config = get_config_loader()
    
    def upload_document(
        self,
        file_content: bytes,
        filename: str,
        country: str,
        document_type: str,
        uploaded_by: str,
        db: Session,
        content_type: str = "application/pdf"
    ) -> models.RAGDocument:
        """
        Upload a document to RAG storage.
        
        Args:
            file_content: Binary content of the file
            filename: Original filename
            country: Country code (SK, IT, DE)
            document_type: Type of document (vseobecne-podmienky, zdravotne, etc.)
            uploaded_by: Username of uploader
            db: Database session
            content_type: MIME type
            
        Returns:
            Created RAGDocument instance
        """
        # Construct S3 key
        s3_key = f"rag/{country}/{document_type}/{filename}"
        
        # Upload to S3
        self.storage_service.upload_bytes(file_content, s3_key, content_type)
        
        # Create database record
        rag_doc = models.RAGDocument(
            filename=filename,
            s3_key=s3_key,
            country=country,
            document_type=document_type,
            uploaded_by=uploaded_by
        )
        
        db.add(rag_doc)
        db.commit()
        db.refresh(rag_doc)
        
        return rag_doc
    
    def process_document(self, rag_doc_id: int, db: Session) -> bool:
        """
        Process RAG document: extract text and generate embedding.
        
        Args:
            rag_doc_id: ID of RAGDocument
            db: Database session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get document
            rag_doc = db.query(models.RAGDocument).filter(
                models.RAGDocument.id == rag_doc_id
            ).first()
            
            if not rag_doc:
                return False
            
            # Download file from S3/MinIO and process as base64
            file_bytes = self.storage_service.download_file_bytes(rag_doc.s3_key)
            
            # Extract text using OCR with base64
            text_content = self.ocr_service.extract_text_from_bytes(file_bytes, rag_doc.filename)
            rag_doc.text_content = text_content
            
            # Generate embedding
            if text_content:
                embedding = self.mistral_service.generate_embedding(text_content)
                if embedding:
                    rag_doc.embedding = embedding
            
            db.commit()
            return True
            
        except Exception as e:
            print(f"Error processing RAG document {rag_doc_id}: {e}")
            db.rollback()
            return False
    
    def search(
        self,
        query_text: str,
        country: str,
        db: Session,
        top_k: Optional[int] = None,
        document_type: Optional[str] = None
    ) -> List[Dict[str, any]]:
        """
        Search for relevant documents using vector similarity.
        
        Args:
            query_text: Text to search for
            country: Country to filter by
            db: Database session
            top_k: Number of results to return (from config if not specified)
            document_type: Optional document type filter
            
        Returns:
            List of relevant documents with metadata and similarity scores
        """
        # Get config
        rag_config = self.config.get_rag_config()
        if top_k is None:
            top_k = rag_config.get("top_k_results", 5)
        
        similarity_threshold = rag_config.get("similarity_threshold", 0.7)
        
        # Generate embedding for query
        query_embedding = self.mistral_service.generate_embedding(query_text)
        if not query_embedding:
            return []
        
        # Build query
        query_parts = [
            "SELECT id, filename, s3_key, country, document_type, text_content,",
            "1 - (embedding <=> :query_embedding) as similarity",
            "FROM rag_documents",
            "WHERE country = :country",
            "AND embedding IS NOT NULL"
        ]
        
        params = {
            "query_embedding": str(query_embedding),
            "country": country,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold
        }
        
        # Add document type filter if specified
        if document_type:
            query_parts.append("AND document_type = :document_type")
            params["document_type"] = document_type
        
        query_parts.extend([
            "AND (1 - (embedding <=> :query_embedding)) >= :similarity_threshold",
            "ORDER BY embedding <=> :query_embedding",
            "LIMIT :top_k"
        ])
        
        query_str = " ".join(query_parts)
        
        # Execute query
        result = db.execute(text(query_str), params)
        rows = result.fetchall()
        
        # Format results
        documents = []
        for row in rows:
            documents.append({
                "id": row[0],
                "filename": row[1],
                "s3_key": row[2],
                "country": row[3],
                "document_type": row[4],
                "text_content": row[5],
                "similarity": float(row[6])
            })
        
        return documents
    
    def get_context_for_claim(
        self,
        claim: models.Claim,
        db: Session,
        max_tokens: int = 8000
    ) -> Tuple[str, List[Dict]]:
        """
        Get relevant context documents for a claim.
        
        Args:
            claim: Claim instance
            db: Database session
            max_tokens: Maximum tokens for context (approximate by chars)
            
        Returns:
            Tuple of (context_string, list_of_source_documents)
        """
        # Aggregate claim text
        claim_texts = []
        for doc in claim.documents:
            if doc.anonymized_text:
                claim_texts.append(doc.anonymized_text)
        
        if not claim_texts:
            return "", []
        
        combined_claim_text = "\n\n".join(claim_texts)
        
        # Search for relevant documents
        relevant_docs = self.search(
            query_text=combined_claim_text,
            country=claim.country,
            db=db
        )
        
        # Build context string (with token limit)
        context_parts = []
        sources = []
        current_length = 0
        max_chars = max_tokens * 4  # Rough estimate: 1 token ≈ 4 chars
        
        for doc in relevant_docs:
            doc_text = doc["text_content"] or ""
            doc_length = len(doc_text)
            
            if current_length + doc_length > max_chars:
                # Truncate to fit
                remaining = max_chars - current_length
                if remaining > 500:  # Only add if meaningful amount fits
                    doc_text = doc_text[:remaining] + "..."
                else:
                    break
            
            context_parts.append(f"[{doc['document_type']} - {doc['filename']}]\n{doc_text}")
            sources.append({
                "filename": doc["filename"],
                "document_type": doc["document_type"],
                "similarity": doc["similarity"]
            })
            
            current_length += len(doc_text)
            
            if current_length >= max_chars:
                break
        
        context_string = "\n\n---\n\n".join(context_parts)
        return context_string, sources
    
    def delete_document(self, rag_doc_id: int, db: Session) -> bool:
        """
        Delete a RAG document (from both S3 and database).
        
        Args:
            rag_doc_id: ID of RAGDocument
            db: Database session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get document
            rag_doc = db.query(models.RAGDocument).filter(
                models.RAGDocument.id == rag_doc_id
            ).first()
            
            if not rag_doc:
                return False
            
            # Delete from S3 (if possible, ignore errors)
            try:
                # Note: S3 delete not implemented in StorageService yet
                # Would need to add: self.storage_service.delete_file(rag_doc.s3_key)
                pass
            except Exception as e:
                print(f"Warning: Could not delete S3 file {rag_doc.s3_key}: {e}")
            
            # Delete from database
            db.delete(rag_doc)
            db.commit()
            return True
            
        except Exception as e:
            print(f"Error deleting RAG document {rag_doc_id}: {e}")
            db.rollback()
            return False
    
    def list_documents(
        self,
        db: Session,
        country: Optional[str] = None,
        document_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[models.RAGDocument]:
        """
        List RAG documents with optional filters.
        
        Args:
            db: Database session
            country: Optional country filter
            document_type: Optional document type filter
            limit: Maximum number of results
            offset: Result offset for pagination
            
        Returns:
            List of RAGDocument instances
        """
        query = db.query(models.RAGDocument)
        
        if country:
            query = query.filter(models.RAGDocument.country == country)
        
        if document_type:
            query = query.filter(models.RAGDocument.document_type == document_type)
        
        query = query.order_by(models.RAGDocument.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        return query.all()
    
    def get_folder_structure(self, db: Session) -> Dict[str, List[str]]:
        """
        Get hierarchical folder structure of RAG documents.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary: {country: [document_types]}
        """
        result = db.execute(
            text("SELECT DISTINCT country, document_type FROM rag_documents ORDER BY country, document_type")
        )
        
        structure = {}
        for row in result:
            country = row[0]
            doc_type = row[1]
            
            if country not in structure:
                structure[country] = []
            
            if doc_type not in structure[country]:
                structure[country].append(doc_type)
        
        return structure
