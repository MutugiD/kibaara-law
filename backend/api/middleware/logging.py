"""
Logging middleware for FastAPI requests.
"""

import time
from fastapi import Request
from loguru import logger


async def log_request_middleware(request: Request, call_next):
    """
    Middleware to log incoming requests and their processing time.

    Args:
        request: FastAPI request object
        call_next: Next middleware or endpoint handler

    Returns:
        Response from the next handler
    """
    start_time = time.time()

    # Log the incoming request
    logger.info(f"Request: {request.method} {request.url}")
    logger.debug(f"Headers: {dict(request.headers)}")

    # Process the request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log the response
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")

    # Add processing time to response headers
    response.headers["X-Process-Time"] = str(process_time)

    return response