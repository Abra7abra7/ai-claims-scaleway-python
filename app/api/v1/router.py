"""
API v1 Router - aggregates all endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    auth,
    claims,
    documents,
    ocr,
    anonymization,
    analysis,
    rag,
    reports,
    audit,
    prompts,
    stats
)

api_router = APIRouter()

# Health check - no prefix, no tag grouping issues
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"]
)

# Authentication
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Claims CRUD
api_router.include_router(
    claims.router,
    prefix="/claims",
    tags=["Claims"]
)

# Documents
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"]
)

# OCR Review - nested under claims
api_router.include_router(
    ocr.router,
    prefix="/claims/{claim_id}/ocr",
    tags=["OCR Review"]
)

# Anonymization Review - nested under claims
api_router.include_router(
    anonymization.router,
    prefix="/claims/{claim_id}/anon",
    tags=["Anonymization"]
)

# Analysis - nested under claims
api_router.include_router(
    analysis.router,
    prefix="/claims/{claim_id}/analysis",
    tags=["Analysis"]
)

# Reports
api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports"]
)

# RAG Management
api_router.include_router(
    rag.router,
    prefix="/rag",
    tags=["RAG Management"]
)

# Prompts
api_router.include_router(
    prompts.router,
    prefix="/prompts",
    tags=["Prompts"]
)

# Audit
api_router.include_router(
    audit.router,
    prefix="/audit",
    tags=["Audit"]
)

# Statistics
api_router.include_router(
    stats.router,
    prefix="/stats",
    tags=["Statistics"]
)

