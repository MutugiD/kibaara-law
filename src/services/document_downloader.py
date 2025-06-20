"""
Document downloader service for downloading case documents.

This module handles downloading of legal documents from various sources
including Kenya Law and other legal databases.
"""

import asyncio
import aiohttp
import os
from typing import Optional, Dict, Any
from loguru import logger
from datetime import datetime
import re
from urllib.parse import urlparse


class DocumentDownloader:
    """
    Service for downloading legal documents from URLs.

    This service handles downloading of case documents, judgments,
    and other legal materials from various sources.
    """

    def __init__(self) -> None:
        """Initialize the document downloader."""
        self.session_timeout = 30
        self.max_retries = 3
        self.retry_delay = 1.0
        self.download_dir = "downloads"
        self.ensure_download_dir()

    def ensure_download_dir(self) -> None:
        """Ensure the download directory exists."""
        os.makedirs(self.download_dir, exist_ok=True)

    async def download_document(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Download a document from a URL.

        Args:
            url: The URL of the document to download

        Returns:
            Dictionary containing document information and content
        """
        if not url:
            logger.warning("No URL provided for document download")
            return None

        logger.info(f"Downloading document from: {url}")

        try:
            # Validate URL
            if not self._is_valid_url(url):
                logger.error(f"Invalid URL: {url}")
                return None

            # Download the document
            content = await self._download_content(url)
            if not content:
                logger.error(f"Failed to download content from: {url}")
                return None

            # Extract document metadata
            metadata = self._extract_metadata(url, content)

            # Save document to file
            filename = self._save_document(url, content)

            document_info = {
                "url": url,
                "content": content,
                "metadata": metadata,
                "filename": filename,
                "download_timestamp": datetime.now().isoformat(),
                "content_length": len(content)
            }

            logger.info(f"Successfully downloaded document: {filename}")
            return document_info

        except Exception as e:
            logger.error(f"Error downloading document from {url}: {str(e)}")
            return None

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    async def _download_content(self, url: str) -> Optional[str]:
        """Download content from URL with retries."""
        for attempt in range(self.max_retries):
            try:
                timeout = aiohttp.ClientTimeout(total=self.session_timeout)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            content = await response.text()
                            logger.info(f"Downloaded {len(content)} characters from {url}")
                            return content
                        else:
                            logger.warning(f"HTTP {response.status} for {url}")

            except asyncio.TimeoutError:
                logger.warning(f"Timeout downloading {url} (attempt {attempt + 1})")
            except Exception as e:
                logger.warning(f"Error downloading {url} (attempt {attempt + 1}): {str(e)}")

            if attempt < self.max_retries - 1:
                await asyncio.sleep(self.retry_delay * (attempt + 1))

        return None

    def _extract_metadata(self, url: str, content: str) -> Dict[str, Any]:
        """Extract metadata from document content."""
        metadata = {
            "source_url": url,
            "content_type": "text/html",
            "extracted_at": datetime.now().isoformat()
        }

        # Try to extract title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if title_match:
            metadata["title"] = title_match.group(1).strip()

        # Try to extract case number
        case_number_patterns = [
            r'Case\s+No\.?\s*([A-Za-z0-9\s\-/]+)',
            r'Civil\s+Appeal\s+([0-9]+)',
            r'Criminal\s+Appeal\s+([0-9]+)',
            r'Petition\s+([A-Za-z0-9\s\-/]+)'
        ]

        for pattern in case_number_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                metadata["case_number"] = match.group(1).strip()
                break

        # Try to extract court name
        court_patterns = [
            r'Court\s+of\s+Appeal',
            r'High\s+Court',
            r'Supreme\s+Court',
            r'Magistrate[^s]*\s+Court'
        ]

        for pattern in court_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                metadata["court"] = match.group(0)
                break

        return metadata

    def _save_document(self, url: str, content: str) -> str:
        """Save document content to file."""
        # Generate filename from URL
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')

        if path_parts:
            # Use the last part of the path as filename
            filename = path_parts[-1]
            if not filename or '.' not in filename:
                filename = f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        else:
            filename = f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        # Ensure filename is safe
        filename = re.sub(r'[^\w\-_.]', '_', filename)
        if not filename.endswith('.html'):
            filename += '.html'

        filepath = os.path.join(self.download_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Document saved to: {filepath}")
            return filename
        except Exception as e:
            logger.error(f"Failed to save document: {str(e)}")
            return ""

    async def download_multiple_documents(self, urls: list[str]) -> list[Dict[str, Any]]:
        """
        Download multiple documents concurrently.

        Args:
            urls: List of URLs to download

        Returns:
            List of downloaded document information
        """
        logger.info(f"Downloading {len(urls)} documents concurrently")

        tasks = [self.download_document(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out None results and exceptions
        successful_downloads = []
        for result in results:
            if isinstance(result, dict):
                successful_downloads.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Download failed with exception: {str(result)}")

        logger.info(f"Successfully downloaded {len(successful_downloads)} out of {len(urls)} documents")
        return successful_downloads

    def get_document_summary(self, document_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of downloaded document.

        Args:
            document_info: Document information dictionary

        Returns:
            Summary dictionary
        """
        content = document_info.get('content', '')
        metadata = document_info.get('metadata', {})

        # Extract key information
        summary = {
            "title": metadata.get('title', 'Unknown'),
            "case_number": metadata.get('case_number', 'Unknown'),
            "court": metadata.get('court', 'Unknown'),
            "content_length": len(content),
            "download_timestamp": document_info.get('download_timestamp'),
            "filename": document_info.get('filename', 'Unknown')
        }

        # Try to extract key phrases
        key_phrases = self._extract_key_phrases(content)
        summary["key_phrases"] = key_phrases

        return summary

    def _extract_key_phrases(self, content: str) -> list[str]:
        """Extract key phrases from document content."""
        # Remove HTML tags
        clean_content = re.sub(r'<[^>]+>', ' ', content)

        # Extract sentences with legal keywords
        legal_keywords = [
            'judgment', 'appeal', 'trial', 'court', 'decision', 'ruling',
            'plaintiff', 'defendant', 'petitioner', 'respondent', 'appellant'
        ]

        sentences = re.split(r'[.!?]+', clean_content)
        key_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and any(keyword in sentence.lower() for keyword in legal_keywords):
                key_sentences.append(sentence[:200] + '...' if len(sentence) > 200 else sentence)

        return key_sentences[:5]  # Return top 5 key sentences