"""
Configuration utility for managing environment variables and settings.

This module handles configuration management for the legal assistant backend,
including API keys, service settings, and environment-specific configurations.
"""

import os
from typing import Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class Config:
    """Configuration class for the legal assistant backend."""

    # OpenAI Configuration
    openai_api_key: str

    # Service Configuration
    max_search_results: int = 10
    max_content_length: int = 50000
    session_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0

    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/legal_assistant.log"

    # Output Configuration
    results_dir: str = "results"

    @classmethod
    def from_env(cls) -> 'Config':
        """
        Create configuration from environment variables.

        Returns:
            Config instance with values from environment variables
        """
        # Required environment variables
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        # Optional environment variables with defaults
        max_search_results = int(os.getenv('MAX_SEARCH_RESULTS', '10'))
        max_content_length = int(os.getenv('MAX_CONTENT_LENGTH', '50000'))
        session_timeout = int(os.getenv('SESSION_TIMEOUT', '30'))
        max_retries = int(os.getenv('MAX_RETRIES', '3'))
        retry_delay = float(os.getenv('RETRY_DELAY', '1.0'))

        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_file = os.getenv('LOG_FILE', 'logs/legal_assistant.log')
        results_dir = os.getenv('RESULTS_DIR', 'results')

        return cls(
            openai_api_key=openai_api_key,
            max_search_results=max_search_results,
            max_content_length=max_content_length,
            session_timeout=session_timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            log_level=log_level,
            log_file=log_file,
            results_dir=results_dir
        )

    def validate(self) -> None:
        """Validate configuration values."""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")

        if self.max_search_results <= 0:
            raise ValueError("max_search_results must be positive")

        if self.max_content_length <= 0:
            raise ValueError("max_content_length must be positive")

        if self.session_timeout <= 0:
            raise ValueError("session_timeout must be positive")

        if self.max_retries <= 0:
            raise ValueError("max_retries must be positive")

        if self.retry_delay <= 0:
            raise ValueError("retry_delay must be positive")

        logger.info("Configuration validation passed")


def get_config() -> Config:
    """
    Get configuration instance.

    Returns:
        Config instance
    """
    try:
        config = Config.from_env()
        config.validate()
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        raise