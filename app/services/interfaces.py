from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class LLMProvider(ABC):
    """Interface for Language Model Providers"""
    
    @abstractmethod
    def analyze_claim(self, claim_text: str, context_documents: List[str], custom_prompt: str = None) -> Dict[str, Any]:
        """Analyze claim text and return structured JSON response"""
        pass

    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for text"""
        pass

class OCRProvider(ABC):
    """Interface for OCR Providers"""
    
    @abstractmethod
    def extract_text_from_url(self, document_url: str) -> str:
        """Extract text from document URL"""
        pass

