from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
import enum
from datetime import datetime

Base = declarative_base()

class ClaimStatus(str, enum.Enum):
    PROCESSING = "PROCESSING"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    APPROVED = "APPROVED"
    ANALYZED = "ANALYZED"
    FAILED = "FAILED"

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default=ClaimStatus.PROCESSING.value)
    analysis_result = Column(JSONB, nullable=True)
    
    documents = relationship("ClaimDocument", back_populates="claim", cascade="all, delete-orphan")

class ClaimDocument(Base):
    __tablename__ = "claim_documents"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"))
    filename = Column(String)
    s3_key = Column(String)
    original_text = Column(Text, nullable=True)
    anonymized_text = Column(Text, nullable=True)
    embedding = Column(Vector(1024), nullable=True)

    claim = relationship("Claim", back_populates="documents")
