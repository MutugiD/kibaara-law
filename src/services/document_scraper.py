"""
Document scraper service for downloading and parsing case documents.

This module handles the downloading and parsing of legal case documents
from various sources identified by the LLM service.
"""

import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from loguru import logger
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime

from ..models.case_models import Case, CaseMetadata, LitigationHop, CourtLevel, CaseStatus


class DocumentScraper:
    """
    Service for downloading and parsing legal case documents.

    This service handles the downloading and extraction of case content
    from URLs provided by the LLM service.
    """

    def __init__(self) -> None:
        """Initialize the document scraper."""
        self.session_timeout = 30
        self.max_retries = 3
        self.retry_delay = 1.0
        self.max_content_length = 50000  # Limit content length
        self.session = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.session_timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def download_case_document(self, case_url: str, case_title: str) -> Optional[Dict[str, Any]]:
        """
        Download and parse a case document from URL.

        Args:
            case_url: URL of the case document
            case_title: Title of the case

        Returns:
            Dictionary containing parsed case data
        """
        logger.info(f"Downloading case document: {case_title}")

        try:
            # Download document content
            content = await self._download_content(case_url)
            if not content:
                logger.error(f"Failed to download content from: {case_url}")
                return None

            # Parse document content
            parsed_data = await self._parse_document_content(content, case_title, case_url)

            logger.info(f"Successfully downloaded and parsed: {case_title}")
            return parsed_data

        except Exception as e:
            logger.error(f"Failed to download case document {case_title}: {str(e)}")
            return None

    async def download_multiple_documents(self, case_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Download multiple case documents concurrently.

        Args:
            case_data: List of case data dictionaries with URLs

        Returns:
            List of downloaded and parsed case documents
        """
        logger.info(f"Downloading {len(case_data)} case documents")

        tasks = []
        for case in case_data:
            if case.get('url'):
                task = self.download_case_document(case['url'], case['title'])
                tasks.append(task)

        # Execute downloads concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failed downloads
        successful_results = []
        for result in results:
            if isinstance(result, dict) and result:
                successful_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Download failed with exception: {str(result)}")

        logger.info(f"Successfully downloaded {len(successful_results)} documents")
        return successful_results

    async def _download_content(self, url: str) -> Optional[str]:
        """Download content from URL."""
        if not self.session:
            logger.error("Session not initialized")
            return None

        for attempt in range(self.max_retries):
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        return content[:self.max_content_length]  # Limit content length
                    else:
                        logger.warning(f"HTTP {response.status} for URL: {url}")

            except Exception as e:
                logger.warning(f"Download attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))

        return None

    async def _parse_document_content(self, content: str, case_title: str, case_url: str) -> Dict[str, Any]:
        """Parse document content and extract case information."""
        try:
            soup = BeautifulSoup(content, 'html.parser')

            # Extract text content
            text_content = self._extract_text_content(soup)

            # Extract metadata
            metadata = self._extract_metadata(soup, case_title, case_url)

            # Extract case structure
            case_structure = self._extract_case_structure(text_content)

            return {
                "title": case_title,
                "url": case_url,
                "content": text_content,
                "metadata": metadata,
                "structure": case_structure,
                "download_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to parse document content: {str(e)}")
            return {
                "title": case_title,
                "url": case_url,
                "content": content[:1000],  # Fallback to raw content
                "metadata": {},
                "structure": {},
                "download_timestamp": datetime.now().isoformat()
            }

    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from HTML."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text content
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text

    def _extract_metadata(self, soup: BeautifulSoup, case_title: str, case_url: str) -> Dict[str, Any]:
        """Extract metadata from document."""
        metadata = {
            "title": case_title,
            "url": case_url,
            "source": self._extract_source(case_url)
        }

        # Try to extract case number
        case_number = self._extract_case_number(soup, case_title)
        if case_number:
            metadata["case_number"] = case_number

        # Try to extract date
        date = self._extract_date(soup)
        if date:
            metadata["date"] = date

        # Try to extract court level
        court_level = self._extract_court_level(soup, case_title)
        if court_level:
            metadata["court_level"] = court_level

        return metadata

    def _extract_source(self, url: str) -> str:
        """Extract source from URL."""
        parsed = urlparse(url)
        return parsed.netloc

    def _extract_case_number(self, soup: BeautifulSoup, case_title: str) -> Optional[str]:
        """Extract case number from document."""
        # Look for common case number patterns
        case_number_patterns = [
            r'Case No\.?\s*([A-Z0-9\/\-]+)',
            r'Civil Case No\.?\s*([A-Z0-9\/\-]+)',
            r'Criminal Case No\.?\s*([A-Z0-9\/\-]+)',
            r'Appeal No\.?\s*([A-Z0-9\/\-]+)',
            r'Petition No\.?\s*([A-Z0-9\/\-]+)'
        ]

        # Search in title first
        for pattern in case_number_patterns:
            match = re.search(pattern, case_title, re.IGNORECASE)
            if match:
                return match.group(1)

        # Search in document content
        text_content = soup.get_text()
        for pattern in case_number_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract date from document."""
        # Look for common date patterns
        date_patterns = [
            r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
            r'(\d{1,2}\/\d{1,2}\/\d{4})',
            r'(\d{4}-\d{2}-\d{2})'
        ]

        text_content = soup.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _extract_court_level(self, soup: BeautifulSoup, case_title: str) -> Optional[str]:
        """Extract court level from document."""
        court_keywords = {
            "Supreme Court": ["supreme court", "supreme"],
            "Court of Appeal": ["court of appeal", "appeal court"],
            "High Court": ["high court", "high"],
            "Magistrate's Court": ["magistrate", "magistrate's court"],
            "Employment and Labour Relations Court": ["employment", "labour relations"],
            "Environment and Land Court": ["environment", "land court"]
        }

        # Search in title first
        for court, keywords in court_keywords.items():
            for keyword in keywords:
                if keyword.lower() in case_title.lower():
                    return court

        # Search in document content
        text_content = soup.get_text()[:2000]  # Limit search area
        for court, keywords in court_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_content.lower():
                    return court

        return None

    def _extract_case_structure(self, text_content: str) -> Dict[str, Any]:
        """Extract case structure and key sections."""
        structure = {
            "parties": self._extract_parties(text_content),
            "claims": self._extract_claims(text_content),
            "decisions": self._extract_decisions(text_content),
            "legal_principles": self._extract_legal_principles(text_content)
        }

        return structure

    def _extract_parties(self, text_content: str) -> List[str]:
        """Extract parties from case content."""
        # Look for party patterns
        party_patterns = [
            r'(?:Plaintiff|Appellant|Petitioner):\s*([^\.]+)',
            r'(?:Defendant|Respondent):\s*([^\.]+)',
            r'([A-Z][A-Z\s&]+)\s+v\.\s+([A-Z][A-Z\s&]+)'
        ]

        parties = []
        for pattern in party_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    parties.extend([p.strip() for p in match if p.strip()])
                else:
                    parties.append(match.strip())

        return list(set(parties))  # Remove duplicates

    def _extract_claims(self, text_content: str) -> List[str]:
        """Extract claims from case content."""
        # Look for claim patterns
        claim_keywords = ["claim", "alleged", "contended", "argued", "submitted"]
        claims = []

        sentences = text_content.split('.')
        for sentence in sentences:
            for keyword in claim_keywords:
                if keyword.lower() in sentence.lower():
                    claims.append(sentence.strip())
                    break

        return claims[:10]  # Limit to 10 claims

    def _extract_decisions(self, text_content: str) -> List[str]:
        """Extract decisions from case content."""
        # Look for decision patterns
        decision_keywords = ["held", "decided", "ruled", "judgment", "order"]
        decisions = []

        sentences = text_content.split('.')
        for sentence in sentences:
            for keyword in decision_keywords:
                if keyword.lower() in sentence.lower():
                    decisions.append(sentence.strip())
                    break

        return decisions[:10]  # Limit to 10 decisions

    def _extract_legal_principles(self, text_content: str) -> List[str]:
        """Extract legal principles from case content."""
        # Look for legal principle patterns
        principle_keywords = ["principle", "doctrine", "rule", "established", "precedent"]
        principles = []

        sentences = text_content.split('.')
        for sentence in sentences:
            for keyword in principle_keywords:
                if keyword.lower() in sentence.lower():
                    principles.append(sentence.strip())
                    break

        return principles[:10]  # Limit to 10 principles