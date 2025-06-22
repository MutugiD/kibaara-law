"""
Dependency injection for FastAPI services.
"""

from .services import get_serp_search_service, get_pdf_downloader_service, get_cache_service

__all__ = [
    "get_serp_search_service",
    "get_pdf_downloader_service",
    "get_cache_service"
]