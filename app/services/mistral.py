"""
Mistral AI Service for claim analysis.
Uses the latest Mistral API with JSON mode support.
API Reference: https://docs.mistral.ai/api
"""
from mistralai import Mistral
from app.core.config import get_settings
from app.services.interfaces import LLMProvider
from typing import List, Dict, Any
import json
import logging

settings = get_settings()

class MistralService(LLMProvider):
    # Available Mistral models
    AVAILABLE_MODELS = {
        "small": "mistral-small-latest",      # Fast, cost-effective
        "medium": "mistral-medium-latest",    # Balanced
        "large": "mistral-large-latest",      # Most capable
    }
    
    def __init__(self):
        self.client = Mistral(api_key=settings.MISTRAL_API_KEY)
        
        # Use configured model or default to LARGE (most capable for analysis)
        configured_model = settings.LLM_MODEL_VERSION
        if configured_model and "mistral" in configured_model.lower():
            self.model = configured_model
        else:
            self.model = "mistral-large-latest"  # Best model for claim analysis
        
        # Embedding model - 1024 dimensions
        self.embedding_model = "mistral-embed"
        
        logging.info(f"Initialized MistralService with model: {self.model}, embedding: {self.embedding_model}")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generates vector embeddings for the given text.
        Uses mistral-embed model.
        """
        try:
            # Truncate if necessary (mistral-embed has 8k token limit)
            truncated_text = text[:8000] 
            
            embeddings_response = self.client.embeddings.create(
                model=self.embedding_model,
                inputs=[truncated_text],
            )
            return embeddings_response.data[0].embedding
        except Exception as e:
            logging.error(f"Error generating embedding: {e}")
            return []

    def analyze_claim(self, claim_text: str, context_documents: List[str], custom_prompt: str = None) -> Dict[str, Any]:
        """
        Analyzes the claim against the provided context documents.
        Uses JSON mode for structured output.
        """
        context_str = "\n\n".join(context_documents) if context_documents else "No specific policy documents provided."
        
        # Use custom prompt if provided, otherwise use default
        if custom_prompt:
            # Replace placeholders in custom prompt
            prompt = custom_prompt.replace("{context}", context_str).replace("{claim_text}", claim_text)
        else:
            # Default prompt
            prompt = f"""
You are an expert insurance claim adjuster. Your task is to analyze the following claim based on the provided policy documents.

POLICY DOCUMENTS:
{context_str}

CLAIM DETAILS:
{claim_text}

Analyze the claim and provide a JSON output with the following fields:
- recommendation: "APPROVE", "REJECT", or "INVESTIGATE"
- confidence: A score between 0.0 and 1.0
- reasoning: A detailed explanation of your decision citing specific parts of the policy.
- missing_info: List of any missing information if applicable.

Return ONLY valid JSON.
"""
        
        try:
            chat_response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert insurance claim analyst. Always respond with valid JSON."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.2,  # Lower for more consistent outputs
            )
            
            content = chat_response.choices[0].message.content
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing Mistral response as JSON: {e}")
            # Try to extract JSON from response
            try:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass
            return {
                "recommendation": "ERROR",
                "reasoning": "Failed to parse AI response as JSON",
                "confidence": 0.0,
                "missing_info": []
            }
        except Exception as e:
            logging.error(f"Error analyzing claim with Mistral: {e}")
            return {
                "recommendation": "ERROR",
                "reasoning": f"AI Analysis failed: {str(e)}",
                "confidence": 0.0,
                "missing_info": []
            }
