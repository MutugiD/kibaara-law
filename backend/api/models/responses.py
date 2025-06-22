"""
Pydantic response models for API endpoints.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AppellateCourt(BaseModel):
    """Model for appellate court information."""

    court: str = Field(..., description="Court name")
    case_number: str = Field(..., description="Case number")
    date: str = Field(..., description="Case date")
    url: str = Field(..., description="Case URL")


class TrialReference(BaseModel):
    """Model for trial court reference."""

    court: str = Field(..., description="Trial court name")
    case_number: str = Field(..., description="Trial case number")
    date: str = Field(..., description="Trial date")


class SearchResult(BaseModel):
    """Model for individual search result."""

    title: str = Field(..., description="Case title")
    appellate_court: AppellateCourt = Field(..., description="Appellate court information")
    trial_reference: TrialReference = Field(..., description="Trial court reference")
    description: str = Field(..., description="Case description")
    confidence: str = Field(..., description="Search confidence level")


class SearchResponse(BaseModel):
    """Response model for case search endpoint."""

    success: bool = Field(..., description="Whether the search was successful")
    results: List[SearchResult] = Field(..., description="Search results")
    total_count: int = Field(..., description="Total number of results")
    query: str = Field(..., description="Original search query")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Search timestamp")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "results": [
                    {
                        "title": "Civil Appeal 232 of 2016 - Nairobi",
                        "appellate_court": {
                            "court": "Court of Appeal",
                            "case_number": "Civil Appeal 232 of 2016",
                            "date": "Not specified",
                            "url": "https://kenyalaw.org/caselaw/cases/view/194677/"
                        },
                        "trial_reference": {
                            "court": "High Court",
                            "case_number": "Not specified",
                            "date": "Not specified"
                        },
                        "description": "The appellate court reviewed the findings of a trial court regarding the award of damages.",
                        "confidence": "Medium"
                    }
                ],
                "total_count": 1,
                "query": "civil appeal damages award",
                "timestamp": "2025-01-21T10:00:00Z"
            }
        }


class PDFFile(BaseModel):
    """Model for PDF file information."""

    filename: str = Field(..., description="PDF filename")
    filepath: str = Field(..., description="File path")
    type: str = Field(..., description="PDF type (standard or with_metadata)")
    url: str = Field(..., description="Download URL")
    size: int = Field(..., description="File size in bytes")
    cached: bool = Field(..., description="Whether file was cached")


class DownloadResult(BaseModel):
    """Model for individual download result."""

    case_title: str = Field(..., description="Case title")
    success: bool = Field(..., description="Whether download was successful")
    pdfs_downloaded: int = Field(..., description="Number of PDFs downloaded")
    total_pdfs_found: int = Field(..., description="Total PDFs found")
    pdf_files: List[PDFFile] = Field(..., description="List of downloaded PDF files")
    appellate_url: str = Field(..., description="Appellate court URL")
    download_timestamp: datetime = Field(..., description="Download timestamp")
    error: Optional[str] = Field(None, description="Error message if download failed")


class DownloadResponse(BaseModel):
    """Response model for PDF download endpoint."""

    success: bool = Field(..., description="Whether the download operation was successful")
    downloads: List[DownloadResult] = Field(..., description="Download results")
    total_cases: int = Field(..., description="Total number of cases processed")
    successful_downloads: int = Field(..., description="Number of successful downloads")
    failed_downloads: int = Field(..., description="Number of failed downloads")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Operation timestamp")


class CaseMetadata(BaseModel):
    """Model for case metadata."""

    case_id: str = Field(..., description="Unique case identifier")
    title: str = Field(..., description="Case title")
    court_level: str = Field(..., description="Court level")
    case_number: str = Field(..., description="Case number")
    date: str = Field(..., description="Case date")
    url: str = Field(..., description="Case URL")
    has_pdf: bool = Field(..., description="Whether PDF is available")
    pdf_count: int = Field(..., description="Number of PDF files")
    cached_at: Optional[datetime] = Field(None, description="When case was cached")


class CaseMetadataResponse(BaseModel):
    """Response model for raw case data endpoint."""

    success: bool = Field(..., description="Whether the operation was successful")
    cases: List[CaseMetadata] = Field(..., description="List of case metadata")
    total_count: int = Field(..., description="Total number of cases")
    filters_applied: Dict[str, Any] = Field(..., description="Filters applied to the query")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Operation timestamp")


class ErrorResponse(BaseModel):
    """Standard error response model."""

    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")