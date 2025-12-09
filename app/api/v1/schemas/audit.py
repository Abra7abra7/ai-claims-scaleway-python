"""
Audit log schemas for API v1.
"""
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from .base import BaseSchema, PaginatedResponse


# ==================== Audit Log Schemas ====================

class AuditLogBase(BaseSchema):
    """Base audit log schema."""
    id: int
    user: str
    action: str
    entity_type: str
    entity_id: int
    timestamp: Optional[datetime] = None


class AuditLogSummary(AuditLogBase):
    """Summary for list endpoints."""
    pass


class AuditLogDetail(AuditLogBase):
    """Full audit log with changes."""
    changes: Optional[dict[str, Any]] = None


class AuditLogListResponse(PaginatedResponse):
    """Paginated list of audit logs."""
    items: list[AuditLogDetail]


# ==================== Query Parameters ====================

class AuditLogQuery(BaseModel):
    """Query parameters for audit logs."""
    entity_type: Optional[str] = Field(
        None,
        description="Filter by entity type (Claim, ClaimDocument, RAGDocument)"
    )
    entity_id: Optional[int] = Field(
        None,
        description="Filter by entity ID"
    )
    user: Optional[str] = Field(
        None,
        description="Filter by username"
    )
    action: Optional[str] = Field(
        None,
        description="Filter by action type"
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of results"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Offset for pagination"
    )


# ==================== Audit Trail ====================

class ClaimAuditTrail(BaseModel):
    """Complete audit trail for a claim."""
    claim_id: int
    events: list[AuditLogDetail]
    total_events: int

