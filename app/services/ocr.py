"""
Mistral OCR Service for document text extraction.
Uses the latest Mistral OCR API.
API Reference: https://docs.mistral.ai/api/endpoint/ocr
"""
from mistralai import Mistral
from app.core.config import get_settings
from app.services.interfaces import OCRProvider
from typing import List, Optional
import base64
import logging

settings = get_settings()

class OCRService(OCRProvider):
    # Latest Mistral OCR model
    OCR_MODEL = "mistral-ocr-latest"  # or "mistral-ocr-2503-completion"
    
    def __init__(self):
        self.client = Mistral(api_key=settings.MISTRAL_API_KEY)
        logging.info(f"Initialized OCRService with model: {self.OCR_MODEL}")

    def extract_text_from_url(self, document_url: str) -> str:
        """
        Extracts text from a document using Mistral OCR API.
        Note: This only works with publicly accessible URLs.
        
        API: POST /v1/ocr
        """
        try:
            ocr_response = self.client.ocr.process(
                model=self.OCR_MODEL,
                document={
                    "type": "document_url",
                    "document_url": document_url
                },
                include_image_base64=False
            )
            
            # Combine text from all pages
            full_text = self._extract_text_from_response(ocr_response)
            return full_text
            
        except Exception as e:
            logging.error(f"Error extracting text with Mistral OCR (URL): {e}")
            return ""
    
    def extract_text_from_bytes(self, file_bytes: bytes, filename: str = "document.pdf") -> str:
        """
        Extracts text from a document using Mistral OCR API.
        Sends the file as base64 encoded data URL.
        
        Supports: PDF, PNG, JPG, JPEG, GIF, WEBP
        """
        try:
            # Encode file to base64
            file_base64 = base64.standard_b64encode(file_bytes).decode("utf-8")
            
            # Determine MIME type based on filename
            mime_type = self._get_mime_type(filename)
            
            # Create data URL (works like a URL but embeds the data)
            data_url = f"data:{mime_type};base64,{file_base64}"
            
            ocr_response = self.client.ocr.process(
                model=self.OCR_MODEL,
                document={
                    "type": "document_url",
                    "document_url": data_url
                },
                include_image_base64=False
            )
            
            # Combine text from all pages
            full_text = self._extract_text_from_response(ocr_response)
            
            logging.info(f"OCR completed for {filename}: {len(full_text)} characters extracted")
            return full_text
            
        except Exception as e:
            logging.error(f"Error extracting text with Mistral OCR (base64): {e}")
            return ""
    
    def extract_text_from_file(self, file_path: str) -> str:
        """
        Extracts text from a local file using Mistral OCR API.
        Reads the file and sends as base64.
        """
        try:
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            
            filename = file_path.split('/')[-1].split('\\')[-1]
            return self.extract_text_from_bytes(file_bytes, filename)
            
        except Exception as e:
            logging.error(f"Error reading file for OCR: {e}")
            return ""
    
    def extract_text_with_pages(self, file_bytes: bytes, filename: str = "document.pdf", 
                                 pages: Optional[List[int]] = None) -> dict:
        """
        Extracts text with page-level information.
        
        Args:
            file_bytes: File content as bytes
            filename: Original filename for MIME type detection
            pages: Optional list of specific page numbers to process (0-indexed)
        
        Returns:
            Dict with 'pages' list and 'full_text' combined text
        """
        try:
            file_base64 = base64.standard_b64encode(file_bytes).decode("utf-8")
            mime_type = self._get_mime_type(filename)
            data_url = f"data:{mime_type};base64,{file_base64}"
            
            # Build request params
            params = {
                "model": self.OCR_MODEL,
                "document": {
                    "type": "document_url",
                    "document_url": data_url
                },
                "include_image_base64": False
            }
            
            # Add page filter if specified
            if pages:
                params["pages"] = pages
            
            ocr_response = self.client.ocr.process(**params)
            
            # Extract page-level information
            pages_data = []
            full_text = ""
            
            for page in ocr_response.pages:
                page_info = {
                    "page_number": page.index if hasattr(page, 'index') else len(pages_data),
                    "text": page.markdown,
                    "dimensions": {
                        "width": page.dimensions.width if hasattr(page, 'dimensions') else None,
                        "height": page.dimensions.height if hasattr(page, 'dimensions') else None,
                    }
                }
                pages_data.append(page_info)
                full_text += page.markdown + "\n\n"
            
            return {
                "pages": pages_data,
                "full_text": full_text.strip(),
                "total_pages": len(pages_data),
                "model": ocr_response.model if hasattr(ocr_response, 'model') else self.OCR_MODEL
            }
            
        except Exception as e:
            logging.error(f"Error extracting text with pages: {e}")
            return {
                "pages": [],
                "full_text": "",
                "total_pages": 0,
                "error": str(e)
            }
    
    def _extract_text_from_response(self, ocr_response) -> str:
        """
        Extracts combined text from OCR response.
        """
        full_text = ""
        for page in ocr_response.pages:
            full_text += page.markdown + "\n\n"
        return full_text.strip()
    
    def _get_mime_type(self, filename: str) -> str:
        """
        Determines MIME type based on file extension.
        """
        extension = filename.lower().split('.')[-1] if '.' in filename else 'pdf'
        mime_types = {
            'pdf': 'application/pdf',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'tiff': 'image/tiff',
            'tif': 'image/tiff',
            'bmp': 'image/bmp',
        }
        return mime_types.get(extension, 'application/pdf')
