from mistralai import Mistral
from app.core.config import get_settings
import os

settings = get_settings()

class OCRService:
    def __init__(self):
        self.client = Mistral(api_key=settings.MISTRAL_API_KEY)

    def extract_text_from_url(self, document_url: str) -> str:
        """
        Extracts text from a document using Mistral Document AI (OCR).
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
