from mistralai import Mistral
from app.core.config import get_settings
from app.services.interfaces import OCRProvider
import os
import base64

settings = get_settings()

class OCRService(OCRProvider):
    def __init__(self):
        self.client = Mistral(api_key=settings.MISTRAL_API_KEY)

    def extract_text_from_url(self, document_url: str) -> str:
        """
        Legacy method - kept for backward compatibility.
        Use extract_text() instead for better reliability.
        """
        try:
            ocr_response = self.client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": document_url
                },
                include_image_base64=False
            )
            
            # Combine text from all pages
            full_text = ""
            for page in ocr_response.pages:
                full_text += page.markdown + "\n\n"
                
            return full_text
        except Exception as e:
            print(f"Error extracting text with Mistral OCR: {e}")
            return ""
    
    def extract_text(self, file_content: bytes, mime_type: str = "application/pdf") -> str:
        """
        Extract text from document using Mistral OCR with base64 upload.
        This method works with local MinIO/S3 storage.
        
        Args:
            file_content: Raw bytes of the document
            mime_type: MIME type of the document (default: application/pdf)
            
        Returns:
            Extracted text in markdown format
        """
        try:
            # Convert to base64
            base64_content = base64.b64encode(file_content).decode('utf-8')
            
            # Create data URI
            data_uri = f"data:{mime_type};base64,{base64_content}"
            
            # Determine document type based on MIME type
            if mime_type.startswith("image/"):
                document_data = {
                    "type": "image_url",
                    "image_url": data_uri
                }
            else:  # PDF or other documents
                document_data = {
                    "type": "document_url",
                    "document_url": data_uri
                }
            
            ocr_response = self.client.ocr.process(
                model="mistral-ocr-latest",
                document=document_data,
                include_image_base64=False
            )
            
            # Combine text from all pages
            full_text = ""
            for page in ocr_response.pages:
                full_text += page.markdown + "\n\n"
                
            return full_text.strip()
            
        except Exception as e:
            print(f"Error extracting text with Mistral OCR: {e}")
            return ""
