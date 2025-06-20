"""
Data models for the Legal Assistant system.

This package contains Pydantic models for data validation and serialization.
"""

from .case_models import Case, LitigationHop, CaseMetadata
from .prompt_models import Prompt, SearchCriteria, AnalysisRequest
from .result_models import AnalysisResult, SearchResult

__all__ = [
    "Case",
    "LitigationHop",
    "CaseMetadata",
    "Prompt",
    "SearchCriteria",
    "AnalysisRequest",
    "AnalysisResult",
    "SearchResult"
]