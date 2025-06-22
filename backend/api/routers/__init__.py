"""
FastAPI routers for different API endpoints.
"""

from .cases import router as cases_router

__all__ = ["cases_router"]