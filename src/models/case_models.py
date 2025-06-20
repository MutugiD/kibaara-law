"""
Case-related data models for legal case representation.

This module contains Pydantic models for representing legal cases,
litigation hops, and case metadata.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


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


class LitigationHop(BaseModel):
    """
    Represents a single step in the litigation process.

    This model tracks the progression of a case through different court levels,
    including the court level, case number, dates, and outcomes.
    """

    court_level: CourtLevel = Field(..., description="The court level for this litigation hop")
    case_number: str = Field(..., description="The case number at this court level")
    filing_date: Optional[datetime] = Field(None, description="Date when case was filed")
    decision_date: Optional[datetime] = Field(None, description="Date when decision was made")
    status: CaseStatus = Field(..., description="Current status of the case at this level")
    outcome: Optional[str] = Field(None, description="Brief description of the outcome")
    judge: Optional[str] = Field(None, description="Name of the presiding judge")
    court_location: Optional[str] = Field(None, description="Location of the court")

    @validator('case_number')
    def validate_case_number(cls, v: str) -> str:
        """Validate that case number is not empty."""
        if not v or not v.strip():
            raise ValueError("Case number cannot be empty")
        return v.strip()


class CaseMetadata(BaseModel):
    """
    Metadata information for a legal case.

    This model contains essential information about a case including
    parties, dates, citations, and basic case information.
    """

    case_title: str = Field(..., description="Full title of the case")
    citation: Optional[str] = Field(None, description="Legal citation for the case")
    parties: List[str] = Field(default_factory=list, description="List of parties involved")
    subject_matter: Optional[str] = Field(None, description="Subject matter of the case")
    case_type: Optional[str] = Field(None, description="Type of case (civil, criminal, etc.)")
    filing_date: Optional[datetime] = Field(None, description="Original filing date")
    source_url: Optional[str] = Field(None, description="URL to the case on Kenya Law")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")

    @validator('case_title')
    def validate_case_title(cls, v: str) -> str:
        """Validate that case title is not empty."""
        if not v or not v.strip():
            raise ValueError("Case title cannot be empty")
        return v.strip()


class Case(BaseModel):
    """
    Complete representation of a legal case.

    This model represents a full legal case with all its metadata,
    litigation progression, and content. It tracks the complete
    journey of a case through the Kenyan legal system.
    """

    metadata: CaseMetadata = Field(..., description="Case metadata and basic information")
    litigation_hops: List[LitigationHop] = Field(default_factory=list, description="Litigation progression through courts")
    pleadings: Optional[str] = Field(None, description="Case pleadings and claims")
    decisions: Optional[str] = Field(None, description="Court decisions and rulings")
    documents: Dict[str, str] = Field(default_factory=dict, description="Case documents by type")
    related_cases: List[str] = Field(default_factory=list, description="Related case citations")
    tags: List[str] = Field(default_factory=list, description="Case tags for categorization")
    analysis_notes: Optional[str] = Field(None, description="Analysis notes and insights")

    @property
    def is_multi_hop(self) -> bool:
        """Check if the case has multiple litigation hops."""
        return len(self.litigation_hops) > 1

    @property
    def current_court_level(self) -> Optional[CourtLevel]:
        """Get the current (highest) court level for this case."""
        if not self.litigation_hops:
            return None
        return max(self.litigation_hops, key=lambda x: list(CourtLevel).index(x.court_level)).court_level

    @property
    def case_number(self) -> Optional[str]:
        """Get the primary case number."""
        if not self.litigation_hops:
            return None
        return self.litigation_hops[0].case_number

    def add_litigation_hop(self, hop: LitigationHop) -> None:
        """Add a new litigation hop to the case."""
        self.litigation_hops.append(hop)
        # Sort by court level
        self.litigation_hops.sort(key=lambda x: list(CourtLevel).index(x.court_level))

    def get_document(self, document_type: str) -> Optional[str]:
        """Get a specific document by type."""
        return self.documents.get(document_type)

    def add_document(self, document_type: str, content: str) -> None:
        """Add a document to the case."""
        self.documents[document_type] = content

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True