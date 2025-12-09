"""
Prompt template schemas for API v1.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .base import BaseSchema


# ==================== Prompt Schemas ====================

class PromptBase(BaseModel):
    """Base prompt schema."""
    name: str
    description: Optional[str] = None


class PromptCreate(PromptBase):
    """Create new prompt template."""
    template: str = Field(..., description="Prompt template text")
    llm_model: str = Field(
        default="mistral-small-latest",
        description="LLM model to use"
    )


class PromptUpdate(BaseModel):
    """Update prompt template."""
    name: Optional[str] = None
    description: Optional[str] = None
    template: Optional[str] = None
    llm_model: Optional[str] = None


class PromptResponse(BaseSchema):
    """Prompt response schema."""
    id: int
    name: str
    description: Optional[str] = None
    template: str
    llm_model: str
    created_at: Optional[datetime] = None


class PromptSummary(BaseModel):
    """Prompt summary for list endpoints."""
    id: str
    name: str
    description: Optional[str] = None
    llm_model: str


class PromptListResponse(BaseModel):
    """List of available prompts."""
    prompts: list[PromptSummary]
    default: str


# ==================== Prompt Config Schemas ====================

class PromptConfigResponse(BaseModel):
    """Prompt configuration from YAML."""
    prompts: list[PromptSummary]
    default_prompt: str
    available_models: list[str]

