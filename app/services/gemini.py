import google.generativeai as genai
from app.core.config import get_settings
from app.services.interfaces import LLMProvider
from typing import List, Dict, Any
import json
import logging

settings = get_settings()

class GeminiService(LLMProvider):
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set")
            
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Use configured model or default to 1.5 Flash (fast & cheap)
        self.model_name = settings.LLM_MODEL_VERSION or "gemini-1.5-flash"
        self.embedding_model = "models/text-embedding-004"
        
        logging.info(f"Initialized GeminiService with model: {self.model_name}")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generates vector embeddings for the given text using Google's embedding model.
        """
        try:
            # Truncate if necessary (Gemini has large context window but embeddings have limits)
            truncated_text = text[:9000] 
            
            result = genai.embed_content(
                model=self.embedding_model,
                content=truncated_text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error generating embedding with Gemini: {e}")
            return []

    def analyze_claim(self, claim_text: str, context_documents: List[str], custom_prompt: str = None) -> Dict[str, Any]:
        """
        Analyzes the claim against the provided context documents.
        """
        context_str = "\n\n".join(context_documents) if context_documents else "No specific policy documents provided."
        
        # Default Prompt (same structure as Mistral for consistency)
        default_prompt_template = """
        You are an expert insurance claim adjuster. Your task is to analyze the following claim based on the provided policy documents.
        
        POLICY DOCUMENTS:
        {context}
        
        CLAIM DETAILS:
        {claim_text}
        
        Analyze the claim and provide a JSON output with the following fields:
        - recommendation: "APPROVE", "REJECT", or "INVESTIGATE"
        - confidence: A score between 0.0 and 1.0
        - reasoning: A detailed explanation of your decision citing specific parts of the policy.
        - missing_info: List of any missing information if applicable.
        
        Return ONLY the JSON without markdown formatting (no ```json blocks).
        """
        
        # Select prompt
        prompt_template = custom_prompt if custom_prompt else default_prompt_template
        
        # Fill placeholders
        final_prompt = prompt_template.replace("{context}", context_str).replace("{claim_text}", claim_text)
        
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={"response_mime_type": "application/json"}
            )
            
            response = model.generate_content(final_prompt)
            
            # Parse JSON
            return json.loads(response.text)
            
        except Exception as e:
            print(f"Error analyzing claim with Gemini: {e}")
            # Fallback error structure
            return {
                "recommendation": "ERROR", 
                "reasoning": f"AI Analysis failed: {str(e)}",
                "confidence": 0.0,
                "missing_info": []
            }

