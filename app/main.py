"""
AI Claims Processing API - Main Application Entry Point

Enterprise-grade API for GDPR-compliant insurance claims processing.
Version: 1.0.0
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import engine
from app.db.models import Base
from app.api.v1.router import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Runs on startup and shutdown.
    """
    # Startup
    # Create pgvector extension and tables
    with engine.connect() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        connection.commit()
    
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Shutdown
    # Add cleanup logic here if needed


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
## AI Claims Processing API

Enterprise-grade, GDPR-compliant insurance claims processing system.

### Features
- **OCR Processing**: Extract text from PDF documents using Mistral AI
- **Text Cleaning**: Rule-based cleaning of OCR output
- **Anonymization**: PII detection and anonymization using Microsoft Presidio
- **AI Analysis**: Insurance claim analysis using LLM with RAG
- **Human-in-the-Loop**: Review steps for OCR and anonymization
- **Audit Trail**: Complete audit logging for compliance

### Authentication
Currently using header-based authentication (X-User-Id, X-User-Email).
Better Auth integration planned for production.

### API Versioning
All endpoints are versioned under `/api/v1/`.
    """,
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router, prefix="/api/v1")


# Root endpoint - redirect info
@app.get("/", include_in_schema=False)
def root():
    """Root endpoint with API info."""
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs": "/api/v1/docs",
        "redoc": "/api/v1/redoc",
        "openapi": "/api/v1/openapi.json"
    }


# Legacy endpoints for backward compatibility
# These will be deprecated in v2

@app.get("/health", include_in_schema=False)
def legacy_health():
    """Legacy health check - use /api/v1/health instead."""
    return {"status": "healthy", "deprecated": True, "use": "/api/v1/health"}
