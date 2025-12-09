"""
Health check endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis

from app.api.deps import get_database
from app.api.v1.schemas.base import HealthResponse
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health check",
    description="Check if the API and its dependencies are healthy"
)
def health_check(db: Session = Depends(get_database)):
    """
    Health check endpoint.
    Returns status of API and connected services.
    """
    services = {}
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        services["database"] = "healthy"
    except Exception:
        services["database"] = "unhealthy"
    
    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        services["redis"] = "healthy"
    except Exception:
        services["redis"] = "unhealthy"
    
    # Check Presidio
    try:
        import requests
        resp = requests.get("http://presidio:8001/health", timeout=5)
        services["presidio"] = "healthy" if resp.status_code == 200 else "unhealthy"
    except Exception:
        services["presidio"] = "unhealthy"
    
    # Overall status
    overall = "healthy" if all(s == "healthy" for s in services.values()) else "degraded"
    
    return HealthResponse(
        status=overall,
        version="1.0.0",
        services=services
    )


@router.get(
    "/ready",
    summary="Readiness check",
    description="Check if the API is ready to serve requests"
)
def readiness_check():
    """Simple readiness check."""
    return {"status": "ready"}


@router.get(
    "/live",
    summary="Liveness check",
    description="Check if the API is alive"
)
def liveness_check():
    """Simple liveness check."""
    return {"status": "alive"}

