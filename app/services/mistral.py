from mistralai import Mistral
from app.core.config import get_settings
from app.services.interfaces import LLMProvider
from typing import List, Dict, Any
import json

settings = get_settings()

class MistralService(LLMProvider):
    def __init__(self):
        self.client = Mistral(api_key=settings.MISTRAL_API_KEY)
        self.model = "mistral-small-latest"  # Using smaller model to avoid rate limits
        self.embedding_model = "mistral-embed"

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generates vector embeddings for the given text.
        """
        try:
            truncated_text = text[:8000] 
            embeddings_batch_response = self.client.embeddings.create(
                model=self.embedding_model,
                inputs=[truncated_text],
            )
            return embeddings_batch_response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []

    def analyze_claim(self, claim_text: str, context_documents: List[str], custom_prompt: str = None) -> Dict[str, Any]:
        """
        Analyzes the claim against the provided context documents.
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
        
        Return ONLY the JSON.
        """
        
        try:
            chat_response = self.client.chat.complete(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            content = chat_response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"Error analyzing claim: {e}")
            return {"error": str(e)}
