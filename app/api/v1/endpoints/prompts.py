"""
Prompt management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_database
from app.api.v1.schemas.prompts import (
    PromptListResponse,
    PromptSummary,
    PromptConfigResponse
)

router = APIRouter()


@router.get(
    "",
    response_model=PromptListResponse,
    summary="List prompts",
    description="Get list of available analysis prompts"
)
def list_prompts():
    """
    Get list of available analysis prompts.
    """
    from app.prompts import get_prompt_list
    
    prompts_data = get_prompt_list()
    
    return PromptListResponse(
        prompts=[
            PromptSummary(
                id=p["id"],
                name=p["name"],
                description=p.get("description"),
                llm_model=p.get("model", "mistral-small-latest")
            )
            for p in prompts_data.get("prompts", [])
        ],
        default=prompts_data.get("default", "default")
    )


@router.get(
    "/config",
    response_model=PromptConfigResponse,
    summary="Get prompt configuration",
    description="Get detailed prompt configuration from YAML"
)
def get_prompts_config():
    """
    Get prompt configuration from config file.
    """
    from app.core.config_loader import get_config_loader
    
    try:
        config = get_config_loader()
        prompt_data = config.get_prompt_list()
        
        return PromptConfigResponse(
            prompts=[
                PromptSummary(
                    id=p["id"],
                    name=p["name"],
                    description=p.get("description"),
                    llm_model=p.get("model", "mistral-small-latest")
                )
                for p in prompt_data.get("prompts", [])
            ],
            default_prompt=prompt_data.get("default", "default"),
            available_models=[
                "mistral-small-latest",
                "mistral-large-latest",
                "gemini-1.5-flash",
                "gemini-1.5-pro"
            ]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load prompt configuration: {str(e)}"
        )


@router.get(
    "/{prompt_id}",
    summary="Get prompt details",
    description="Get details of a specific prompt"
)
def get_prompt(
    prompt_id: str
):
    """
    Get prompt details by ID.
    """
    from app.prompts import get_prompt_template, get_prompt_list
    
    # Check if prompt exists
    prompts_data = get_prompt_list()
    prompt_info = None
    
    for p in prompts_data.get("prompts", []):
        if p["id"] == prompt_id:
            prompt_info = p
            break
    
    if not prompt_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt '{prompt_id}' not found"
        )
    
    # Get template
    template = get_prompt_template(prompt_id)
    
    return {
        "id": prompt_id,
        "name": prompt_info.get("name"),
        "description": prompt_info.get("description"),
        "template": template,
        "llm_model": prompt_info.get("model", "mistral-small-latest")
    }

