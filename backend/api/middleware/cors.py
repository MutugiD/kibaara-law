"""
CORS middleware configuration for FastAPI.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List


def setup_cors(app: FastAPI, allowed_origins: List[str] = None) -> None:
    """
    Set up CORS middleware for the FastAPI application.

    Args:
        app: FastAPI application instance
        allowed_origins: List of allowed origins for CORS
    """
    if allowed_origins is None:
        allowed_origins = [
            "http://localhost:3000",  # React development server
            "http://localhost:3001",  # Alternative React port
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )