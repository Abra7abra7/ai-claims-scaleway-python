from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Claims Processing"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # Provider Selection
    LLM_PROVIDER: str = "mistral"
    OCR_PROVIDER: str = "mistral"
    
    # Model Configuration
    LLM_MODEL_VERSION: Optional[str] = None  # Specific model version (e.g. "gemini-1.5-pro")
    
    # AI Providers API Keys
    MISTRAL_API_KEY: str
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # S3 / Scaleway Object Storage
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET_NAME: str
    S3_ENDPOINT_URL: str
    S3_REGION: str

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()
