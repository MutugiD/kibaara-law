"""
Result models for search and analysis operations.

This module contains Pydantic models for representing search results,
analysis results, and structured responses from the legal assistant.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .case_models import Case


class SearchResult(BaseModel):
    """
    Result from a legal case search operation.

    This model represents the results of searching for legal cases,
    including metadata and relevance scoring.
    """

    case_url: str = Field(..., description="URL to the case on Kenya Law")
    case_title: str = Field(..., description="Title of the case")
    case_number: Optional[str] = Field(None, description="Case number")
    court_level: Optional[str] = Field(None, description="Court level")
    relevance_score: float = Field(default=0.0, description="Relevance score (0-1)")
    match_reasons: List[str] = Field(default_factory=list, description="Reasons for match")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @property
    def is_relevant(self) -> bool:
        """Check if the result is considered relevant."""
        return self.relevance_score >= 0.5


class AnalysisResult(BaseModel):
    """
    Result from case analysis operation.

    This model represents the complete analysis of a legal case,
    including all extracted information and insights.
    """

    case: Case = Field(..., description="The analyzed case")
    analysis_timestamp: datetime = Field(default_factory=datetime.now, description="When analysis was performed")
    processing_time: float = Field(default=0.0, description="Time taken to process (seconds)")
    confidence_score: float = Field(default=0.0, description="Confidence in analysis (0-1)")
    extraction_notes: List[str] = Field(default_factory=list, description="Notes about data extraction")
    quality_indicators: Dict[str, Any] = Field(default_factory=dict, description="Data quality indicators")

    class Config:
        arbitrary_types_allowed = True

    @property
    def is_high_quality(self) -> bool:
        """Check if the analysis result is high quality."""
        return self.confidence_score >= 0.8


class PromptResponse(BaseModel):
    """
    Complete response to a user prompt.

    This model represents the full response to a user's legal research
    prompt, including all found cases and analysis results.
    """

    prompt_id: str = Field(..., description="Unique identifier for the prompt")
    original_prompt: str = Field(..., description="The original user prompt")
    search_criteria: Dict[str, Any] = Field(..., description="Extracted search criteria")
    search_results: List[SearchResult] = Field(default_factory=list, description="Initial search results")
    analyzed_cases: List[AnalysisResult] = Field(default_factory=list, description="Fully analyzed cases")
    summary: Optional[str] = Field(None, description="Summary of findings")
    statistics: Dict[str, Any] = Field(default_factory=dict, description="Search and analysis statistics")
    processing_time: float = Field(default=0.0, description="Total processing time")
    status: str = Field(default="completed", description="Processing status")
    error_message: Optional[str] = Field(None, description="Error message if any")

    class Config:
        arbitrary_types_allowed = True

    @property
    def case_count(self) -> int:
        """Get the number of analyzed cases."""
        return len(self.analyzed_cases)

    @property
    def multi_hop_cases(self) -> List[AnalysisResult]:
        """Get only multi-hop cases."""
        return [result for result in self.analyzed_cases if result.case.is_multi_hop]

    def get_cases_by_court_level(self, court_level: str) -> List[AnalysisResult]:
        """Get cases by specific court level."""
        return [
            result for result in self.analyzed_cases
            if result.case.current_court_level == court_level
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the results."""
        total_cases = len(self.analyzed_cases)
        multi_hop_count = len(self.multi_hop_cases)

        court_levels = {}
        for result in self.analyzed_cases:
            level = result.case.current_court_level
            if level:
                court_levels[level] = court_levels.get(level, 0) + 1

        return {
            "total_cases": total_cases,
            "multi_hop_cases": multi_hop_count,
            "single_hop_cases": total_cases - multi_hop_count,
            "court_level_distribution": court_levels,
            "average_confidence": sum(r.confidence_score for r in self.analyzed_cases) / total_cases if total_cases > 0 else 0,
            "processing_time": self.processing_time
        }