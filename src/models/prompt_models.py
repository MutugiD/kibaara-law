"""
Prompt processing models for legal research requests.

This module contains Pydantic models for processing user prompts,
extracting search criteria, and managing analysis requests.
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from .case_models import CourtLevel


class LegalPrompt(BaseModel):
    """
    Simple legal prompt model for the new modular approach.

    This model represents a basic legal research prompt
    without complex processing.
    """

    content: str = Field(..., description="The prompt content")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the prompt was created")

    @validator('content')
    def validate_content(cls, v: str) -> str:
        """Validate prompt content is not empty."""
        if not v or not v.strip():
            raise ValueError("Prompt content cannot be empty")
        return v.strip()


class SearchCriteria(BaseModel):
    """
    Search criteria extracted from user prompts.

    This model represents the structured search parameters
    extracted from natural language prompts.
    """

    case_count: int = Field(default=5, description="Number of cases to retrieve")
    court_levels: List[CourtLevel] = Field(default_factory=list, description="Target court levels")
    date_from: Optional[date] = Field(None, description="Start date for case search")
    date_to: Optional[date] = Field(None, description="End date for case search")
    subject_matter: Optional[str] = Field(None, description="Subject matter keywords")
    case_type: Optional[str] = Field(None, description="Type of case (civil, criminal, etc.)")
    parties: List[str] = Field(default_factory=list, description="Party names to search for")
    keywords: List[str] = Field(default_factory=list, description="Additional search keywords")
    require_multi_hop: bool = Field(default=True, description="Require multi-hop litigation")
    min_hops: int = Field(default=2, description="Minimum number of litigation hops")

    @validator('case_count')
    def validate_case_count(cls, v: int) -> int:
        """Validate case count is reasonable."""
        if v < 1:
            raise ValueError("Case count must be at least 1")
        if v > 100:
            raise ValueError("Case count cannot exceed 100")
        return v

    @validator('min_hops')
    def validate_min_hops(cls, v: int) -> int:
        """Validate minimum hops is reasonable."""
        if v < 1:
            raise ValueError("Minimum hops must be at least 1")
        if v > 5:
            raise ValueError("Minimum hops cannot exceed 5")
        return v


class Prompt(BaseModel):
    """
    User prompt for legal research.

    This model represents a user's natural language request
    for legal research and case analysis.
    """

    text: str = Field(..., description="The original prompt text")
    search_criteria: SearchCriteria = Field(..., description="Extracted search criteria")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the prompt was received")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    priority: str = Field(default="normal", description="Request priority level")

    @validator('text')
    def validate_text(cls, v: str) -> str:
        """Validate prompt text is not empty."""
        if not v or not v.strip():
            raise ValueError("Prompt text cannot be empty")
        if len(v) > 2000:
            raise ValueError("Prompt text cannot exceed 2000 characters")
        return v.strip()

    @validator('priority')
    def validate_priority(cls, v: str) -> str:
        """Validate priority level."""
        valid_priorities = ["low", "normal", "high", "urgent"]
        if v not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}")
        return v

    def extract_keywords(self) -> List[str]:
        """Extract keywords from the prompt text."""
        # Simple keyword extraction - can be enhanced with NLP
        words = self.text.lower().split()
        # Remove common words and punctuation
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        keywords = [word.strip(".,!?;:") for word in words if word not in stop_words and len(word) > 2]
        return list(set(keywords))


class AnalysisRequest(BaseModel):
    """
    Request for case analysis.

    This model represents a request to analyze specific cases
    based on extracted search criteria.
    """

    prompt: Prompt = Field(..., description="Original user prompt")
    case_urls: List[str] = Field(default_factory=list, description="URLs of cases to analyze")
    analysis_type: str = Field(default="full", description="Type of analysis to perform")
    include_documents: bool = Field(default=True, description="Include case documents")
    include_related_cases: bool = Field(default=True, description="Include related cases")
    output_format: str = Field(default="json", description="Output format for results")

    @validator('analysis_type')
    def validate_analysis_type(cls, v: str) -> str:
        """Validate analysis type."""
        valid_types = ["basic", "full", "summary", "detailed"]
        if v not in valid_types:
            raise ValueError(f"Analysis type must be one of: {valid_types}")
        return v

    @validator('output_format')
    def validate_output_format(cls, v: str) -> str:
        """Validate output format."""
        valid_formats = ["json", "xml", "csv", "pdf", "text"]
        if v not in valid_formats:
            raise ValueError(f"Output format must be one of: {valid_formats}")
        return v

    def get_analysis_scope(self) -> Dict[str, bool]:
        """Get the scope of analysis to perform."""
        return {
            "metadata": True,
            "litigation_hops": True,
            "pleadings": self.analysis_type in ["full", "detailed"],
            "decisions": True,
            "documents": self.include_documents,
            "related_cases": self.include_related_cases,
            "analysis_notes": self.analysis_type in ["full", "detailed"]
        }