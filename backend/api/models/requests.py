"""
Pydantic request models for API endpoints.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request model for case search endpoint."""

    query: str = Field(..., description="Search query for legal cases", min_length=1, max_length=2000)
    max_results: int = Field(10, description="Maximum number of results to return", ge=1, le=100)
    court_level: Optional[str] = Field(None, description="Filter by court level (magistrate, high, appellate)")

    class Config:
        schema_extra = {
            "example": {
                "query": "civil appeal damages award",
                "max_results": 10,
                "court_level": "appellate"
            }
        }


class DownloadRequest(BaseModel):
    """Request model for PDF download endpoint."""

    case_urls: List[str] = Field(..., description="List of case URLs to download PDFs for", min_items=1)

    class Config:
        schema_extra = {
            "example": {
                "case_urls": [
                    "https://kenyalaw.org/caselaw/cases/view/194677/",
                    "https://kenyalaw.org/caselaw/cases/view/253591/"
                ]
            }
        }


class CaseFilterRequest(BaseModel):
    """Request model for filtering raw case data."""

    court_level: Optional[str] = Field(None, description="Filter by court level")
    date_from: Optional[str] = Field(None, description="Filter cases from this date (YYYY-MM-DD)")
    date_to: Optional[str] = Field(None, description="Filter cases to this date (YYYY-MM-DD)")
    limit: int = Field(50, description="Maximum number of cases to return", ge=1, le=1000)

    class Config:
        schema_extra = {
            "example": {
                "court_level": "appellate",
                "date_from": "2020-01-01",
                "date_to": "2023-12-31",
                "limit": 50
            }
        }