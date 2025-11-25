from app.core.config import get_settings
from app.services.interfaces import LLMProvider, OCRProvider
from app.services.mistral import MistralService
from app.services.ocr import OCRService

# Placeholder classes for future implementation
class NotImplementedService(LLMProvider, OCRProvider):
    def analyze_claim(self, *args, **kwargs):
        return {"error": "Provider not implemented yet"}
    
    def generate_embedding(self, *args, **kwargs):
        return []
        
    def extract_text_from_url(self, *args, **kwargs):
        return "OCR Provider not implemented yet"

def get_llm_service() -> LLMProvider:
    settings = get_settings()
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "mistral":
        return MistralService()
    elif provider == "openai":
        # TODO: Implement OpenAIService
        return NotImplementedService()
    elif provider == "gemini":
        try:
            from app.services.gemini import GeminiService
            return GeminiService()
        except ImportError:
            print("Error: google-generativeai not installed. Please add it to requirements.txt")
            return NotImplementedService()
        except ValueError as e:
            print(f"Error initializing Gemini: {e}")
            return NotImplementedService()
    else:
        print(f"Warning: Unknown LLM provider '{provider}', falling back to Mistral")
        return MistralService()

def get_ocr_service() -> OCRProvider:
    settings = get_settings()
    provider = settings.OCR_PROVIDER.lower()
    
    if provider == "mistral":
        return OCRService()
    elif provider == "google":
        # TODO: Implement GoogleDocumentAI
        return NotImplementedService()
    elif provider == "aws":
        # TODO: Implement TextractService
        return NotImplementedService()
    else:
        print(f"Warning: Unknown OCR provider '{provider}', falling back to Mistral")
        return OCRService()
