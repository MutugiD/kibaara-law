"""
Cache service for storing downloaded cases and analysis results.

This module provides caching functionality to prevent re-downloading
and re-analyzing cases that have already been processed.
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
import hashlib


class CacheService:
    """
    Service for caching case downloads and analysis results.

    This service maintains a JSON-based cache to store:
    - Downloaded case information
    - Analysis results
    - PDF download status
    - Case metadata
    """

    def __init__(self, cache_file: str = "cache/downloaded_cases.json") -> None:
        """
        Initialize the cache service.

        Args:
            cache_file: Path to the JSON cache file
        """
        self.cache_file = cache_file
        self.cache_dir = os.path.dirname(cache_file)

        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)

        # Load existing cache or create new one
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        """
        Load cache from JSON file.

        Returns:
            Cache dictionary
        """
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                logger.info(f"Loaded cache with {len(cache.get('cases', {}))} cases")
                return cache
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")

        # Return empty cache structure
        return {
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            },
            "cases": {},
            "statistics": {
                "total_cases": 0,
                "downloaded_cases": 0,
                "analyzed_cases": 0
            }
        }

    def _save_cache(self) -> None:
        """Save cache to JSON file."""
        try:
            self.cache["metadata"]["last_updated"] = datetime.now().isoformat()
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            logger.info(f"Cache saved with {len(self.cache.get('cases', {}))} cases")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def _generate_case_key(self, case_title: str, appellate_url: str) -> str:
        """
        Generate a unique key for a case.

        Args:
            case_title: Title of the case
            appellate_url: URL of the appellate court decision

        Returns:
            Unique case key
        """
        # Create a hash from case title and URL
        key_string = f"{case_title}:{appellate_url}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def is_case_cached(self, case_title: str, appellate_url: str) -> bool:
        """
        Check if a case is already cached.

        Args:
            case_title: Title of the case
            appellate_url: URL of the appellate court decision

        Returns:
            True if case is cached, False otherwise
        """
        case_key = self._generate_case_key(case_title, appellate_url)
        return case_key in self.cache.get("cases", {})

    def get_cached_case(self, case_title: str, appellate_url: str) -> Optional[Dict[str, Any]]:
        """
        Get cached case information.

        Args:
            case_title: Title of the case
            appellate_url: URL of the appellate court decision

        Returns:
            Cached case data or None if not found
        """
        case_key = self._generate_case_key(case_title, appellate_url)
        cached_case = self.cache.get("cases", {}).get(case_key)

        if cached_case:
            logger.info(f"Found cached case: {case_title}")
            return cached_case

        return None

    def cache_case(self, case_data: Dict[str, Any]) -> None:
        """
        Cache case information.

        Args:
            case_data: Case data to cache
        """
        case_title = case_data.get("title", "Unknown")
        appellate_url = case_data.get("appellate_court", {}).get("url", "")

        if not appellate_url:
            logger.warning(f"Cannot cache case without appellate URL: {case_title}")
            return

        case_key = self._generate_case_key(case_title, appellate_url)

        # Add cache metadata
        case_data["cached_at"] = datetime.now().isoformat()
        case_data["cache_key"] = case_key

        # Store in cache
        self.cache["cases"][case_key] = case_data

        # Update statistics
        self.cache["statistics"]["total_cases"] = len(self.cache["cases"])

        if case_data.get("pdf_downloaded"):
            self.cache["statistics"]["downloaded_cases"] += 1

        if case_data.get("analyzed"):
            self.cache["statistics"]["analyzed_cases"] += 1

        # Save cache
        self._save_cache()

        logger.info(f"Cached case: {case_title}")

    def update_case_analysis(self, case_title: str, appellate_url: str, analysis_data: Dict[str, Any]) -> None:
        """
        Update cached case with analysis results.

        Args:
            case_title: Title of the case
            appellate_url: URL of the appellate court decision
            analysis_data: Analysis results to add
        """
        case_key = self._generate_case_key(case_title, appellate_url)

        if case_key in self.cache.get("cases", {}):
            # Update existing case
            self.cache["cases"][case_key].update(analysis_data)
            self.cache["cases"][case_key]["analyzed"] = True
            self.cache["cases"][case_key]["analysis_updated_at"] = datetime.now().isoformat()

            # Update statistics
            self.cache["statistics"]["analyzed_cases"] = sum(
                1 for case in self.cache["cases"].values() if case.get("analyzed")
            )

            self._save_cache()
            logger.info(f"Updated analysis for cached case: {case_title}")
        else:
            logger.warning(f"Cannot update analysis for non-cached case: {case_title}")

    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Cache statistics dictionary
        """
        return self.cache.get("statistics", {})

    def get_case(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached case by cache key.

        Args:
            cache_key: Cache key for the case

        Returns:
            Cached case data or None if not found
        """
        return self.cache.get("cases", {}).get(cache_key)

    def cache_case(self, cache_key: str, case_data: Dict[str, Any]) -> None:
        """
        Cache case information using a specific cache key.

        Args:
            cache_key: Cache key for the case
            case_data: Case data to cache
        """
        # Add cache metadata
        case_data["cached_at"] = datetime.now().isoformat()
        case_data["cache_key"] = cache_key

        # Store in cache
        self.cache["cases"][cache_key] = case_data

        # Update statistics
        self.cache["statistics"]["total_cases"] = len(self.cache["cases"])

        if case_data.get("pdf_downloaded"):
            self.cache["statistics"]["downloaded_cases"] += 1

        if case_data.get("analyzed"):
            self.cache["statistics"]["analyzed_cases"] += 1

        # Save cache
        self._save_cache()

        logger.info(f"Cached case with key: {cache_key}")

    def is_pdf_cached(self, pdf_filename: str) -> bool:
        """
        Check if a PDF file is already cached.

        Args:
            pdf_filename: Name of the PDF file

        Returns:
            True if PDF is cached, False otherwise
        """
        for case_data in self.cache.get("cases", {}).values():
            if case_data.get("pdf_filename") == pdf_filename:
                return True
        return False

    def get_cached_pdf_analysis(self, pdf_filename: str) -> Optional[Dict[str, Any]]:
        """
        Get cached PDF analysis by filename.

        Args:
            pdf_filename: Name of the PDF file

        Returns:
            Cached PDF analysis or None if not found
        """
        for case_data in self.cache.get("cases", {}).values():
            if case_data.get("pdf_filename") == pdf_filename:
                return case_data
        return None

    def cache_pdf_analysis(self, pdf_filename: str, analysis_data: Dict[str, Any]) -> None:
        """
        Cache PDF analysis results.

        Args:
            pdf_filename: Name of the PDF file
            analysis_data: Analysis results to cache
        """
        cache_key = f"pdf_analysis_{hashlib.md5(pdf_filename.encode()).hexdigest()}"

        # Add cache metadata
        analysis_data["pdf_filename"] = pdf_filename
        analysis_data["cached_at"] = datetime.now().isoformat()
        analysis_data["cache_key"] = cache_key

        # Store in cache
        self.cache["cases"][cache_key] = analysis_data

        # Update statistics
        self.cache["statistics"]["total_cases"] = len(self.cache["cases"])
        self.cache["statistics"]["analyzed_cases"] += 1

        # Save cache
        self._save_cache()

        logger.info(f"Cached PDF analysis: {pdf_filename}")

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self.cache = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            },
            "cases": {},
            "statistics": {
                "total_cases": 0,
                "downloaded_cases": 0,
                "analyzed_cases": 0
            }
        }
        self._save_cache()
        logger.info("Cache cleared")

    def get_all_cached_cases(self) -> List[Dict[str, Any]]:
        """
        Get all cached cases.

        Returns:
            List of all cached cases
        """
        return list(self.cache.get("cases", {}).values())

    def export_cache(self, export_file: str = "cache/cache_export.json") -> None:
        """
        Export cache to a file.

        Args:
            export_file: Path to export file
        """
        try:
            os.makedirs(os.path.dirname(export_file), exist_ok=True)
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            logger.info(f"Cache exported to: {export_file}")
        except Exception as e:
            logger.error(f"Failed to export cache: {e}")