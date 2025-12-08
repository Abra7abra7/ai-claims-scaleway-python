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
        Extracts text from a document using Mistral Document AI (OCR).
        Note: This only works with publicly accessible URLs.
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
    
    def extract_text_from_bytes(self, file_bytes: bytes, filename: str = "document.pdf") -> str:
        """
        Extracts text from a document using Mistral Document AI (OCR).
        Sends the file as base64 encoded data.
        """
        try:
            # Encode file to base64
            file_base64 = base64.standard_b64encode(file_bytes).decode("utf-8")
            
            # Determine MIME type based on filename
            extension = filename.lower().split('.')[-1] if '.' in filename else 'pdf'
            mime_types = {
                'pdf': 'application/pdf',
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'gif': 'image/gif',
                'webp': 'image/webp'
            }
            mime_type = mime_types.get(extension, 'application/pdf')
            
            # Create data URL
            data_url = f"data:{mime_type};base64,{file_base64}"
            
            ocr_response = self.client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": data_url
                },
                include_image_base64=False
            )
            
            # Combine text from all pages
            full_text = ""
            for page in ocr_response.pages:
                full_text += page.markdown + "\n\n"
                
            return full_text
        except Exception as e:
            print(f"Error extracting text with Mistral OCR (base64): {e}")
            return ""
