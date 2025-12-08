"""
Google Gemini AI Service for claim analysis.
Uses the latest Gemini 2.0 models with v1 API.
"""
from google import genai
from google.genai import types
from app.core.config import get_settings
from app.services.interfaces import LLMProvider
from typing import List, Dict, Any
import json
import logging

settings = get_settings()

class GeminiService(LLMProvider):
    # Available Gemini models (2024-2025)
    AVAILABLE_MODELS = [
        "gemini-2.0-flash",       # Latest, fastest
        "gemini-2.0-flash-exp",   # Experimental
        "gemini-1.5-flash",       # Stable
        "gemini-1.5-pro",         # More capable
    ]
    
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set")
        
        # Initialize the new client with v1 API (stable)
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
            http_options={'api_version': 'v1'}
        )
        
        # Use configured model or default to latest
        configured_model = settings.LLM_MODEL_VERSION
        if configured_model and "gemini" in configured_model.lower():
            self.model_name = configured_model
        else:
            # Default to latest fast model
            self.model_name = "gemini-2.0-flash"
            if configured_model:
                logging.warning(f"Model '{configured_model}' may not be valid, using {self.model_name}")
        
        self.embedding_model = "text-embedding-004"
        
        logging.info(f"Initialized GeminiService with model: {self.model_name} (API v1)")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generates vector embeddings for the given text using Google's embedding model.
        """
        try:
            # Truncate if necessary
            truncated_text = text[:9000] 
            
            result = self.client.models.embed_content(
                model=self.embedding_model,
                contents=truncated_text
            )
            return result.embeddings[0].values if result.embeddings else []
        except Exception as e:
            print(f"Error generating embedding with Gemini: {e}")
            return []

    def analyze_claim(self, claim_text: str, context_documents: List[str], custom_prompt: str = None) -> Dict[str, Any]:
        """
        Analyzes the claim against the provided context documents.
        """
        context_str = "\n\n".join(context_documents) if context_documents else "No specific policy documents provided."
        
        # Default Prompt
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
        
        Return ONLY valid JSON without markdown formatting.
        """
        
        # Select prompt
        prompt_template = custom_prompt if custom_prompt else default_prompt_template
        
        # Fill placeholders
        final_prompt = prompt_template.replace("{context}", context_str).replace("{claim_text}", claim_text)
        
        try:
            # Use the new client API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=final_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,  # Lower for more consistent outputs
                )
            )
            
            # Parse JSON response
            return json.loads(response.text)
            
        except json.JSONDecodeError as e:
            print(f"Error parsing Gemini response as JSON: {e}")
            # Try to extract JSON from response
            try:
                import re
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass
            return {
                "recommendation": "ERROR",
                "reasoning": f"Failed to parse AI response as JSON",
                "confidence": 0.0,
                "missing_info": []
            }
        except Exception as e:
            print(f"Error analyzing claim with Gemini: {e}")
            return {
                "recommendation": "ERROR", 
                "reasoning": f"AI Analysis failed: {str(e)}",
                "confidence": 0.0,
                "missing_info": []
            }
