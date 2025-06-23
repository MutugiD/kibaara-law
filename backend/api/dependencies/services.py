"""
Service dependencies for FastAPI application
"""

import os
from typing import Generator
from backend.services.serp_search_service import SerpSearchService
from backend.services.pdf_downloader import PDFDownloader
from backend.services.cache_service import CacheService


def get_serp_search_service() -> SerpSearchService:
    """
    Get SerpSearchService instance with API key from environment.

    Returns:
        SerpSearchService instance
    """
    api_key = os.environ.get("SERP_API_KEY")
    if not api_key:
        raise RuntimeError("SERP_API_KEY environment variable not set.")
    return SerpSearchService(api_key=api_key)


def get_pdf_downloader_service() -> PDFDownloader:
    """
    Get PDFDownloaderService instance.

    Returns:
        PDFDownloaderService instance
    """
    return PDFDownloader()


def get_cache_service() -> CacheService:
    """
    Get CacheService instance.

    Returns:
        CacheService instance
    """
    return CacheService()