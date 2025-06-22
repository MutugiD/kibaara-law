"""
This module defines the SQLAlchemy and Pydantic models for legal cases.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func

from backend.database import Base


class DocumentType(str, Enum):
    """Enumeration for the type of legal document."""
    CASE_LAW = "case_law"
    PLEADINGS = "pleadings"


class CourtLevel(str, Enum):
    """Enumeration of Kenyan court levels."""
    MAGISTRATE = "Magistrate"
    HIGH_COURT = "High Court"
    COURT_OF_APPEAL = "Court of Appeal"
    SUPREME_COURT = "Supreme Court"


class CaseStatus(str, Enum):
    """Enumeration of case statuses."""
    PENDING = "Pending"
    DECIDED = "Decided"
    DISMISSED = "Dismissed"
    SETTLED = "Settled"
    APPEALED = "Appealed"
    UPLOADED = "Uploaded"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"


class Case(Base):
    """
    SQLAlchemy ORM model for a legal case stored in the database.
    """
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True, nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default=CaseStatus.UPLOADED, nullable=False)
    document_type = Column(String, nullable=False)
    analysis_results = Column(JSON, nullable=True)


class CaseBase(BaseModel):
    """Base Pydantic model for a case, used for common attributes."""
    filename: str


class CaseCreate(CaseBase):
    """Pydantic model for creating a new case (API input)."""
    pass


class CaseSchema(CaseBase):
    """Pydantic model for representing a case in the API (API output)."""
    id: int
    upload_date: datetime
    status: str
    document_type: str
    analysis_results: Optional[dict]

    class Config:
        """Pydantic configuration to allow ORM mode."""
        from_attributes = True