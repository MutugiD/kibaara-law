"""
Kenya Law scraper service for downloading case documents and data.

This module handles the scraping and downloading of legal cases from
Kenya Law website, including case documents, pleadings, and rulings.
"""

import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse
import aiohttp
from bs4 import BeautifulSoup
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from ..models.case_models import Case, CaseMetadata, LitigationHop, CourtLevel, CaseStatus


class KenyaLawScraper:
    """
    Service for scraping legal cases from Kenya Law website.

    This service handles the downloading and extraction of case data,
    documents, and metadata from the Kenya Law database.
    """

    def __init__(self) -> None:
        """Initialize the Kenya Law scraper."""
        self.base_url = "https://kenyalaw.org"
        self.search_url = "https://kenyalaw.org/caselaw/cases/"
        self.session_timeout = 30
        self.retry_attempts = 3
        self.delay_between_requests = 1.0

        # Initialize webdriver for JavaScript-heavy pages
        self.driver = None
        self._setup_webdriver()

    def _setup_webdriver(self) -> None:
        """Set up Chrome webdriver for scraping."""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")

            self.driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            logger.info("Chrome webdriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize webdriver: {str(e)}")
            self.driver = None

    async def search_cases(self, search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for cases based on criteria.

        Args:
            search_criteria: Dictionary containing search parameters

        Returns:
            List of case search results
        """
        logger.info(f"Searching for cases with criteria: {search_criteria}")

        try:
            # Build search query
            search_query = self._build_search_query(search_criteria)

            # Perform search
            search_results = await self._perform_search(search_query)

            # Filter results based on criteria
            filtered_results = self._filter_search_results(search_results, search_criteria)

            logger.info(f"Found {len(filtered_results)} cases matching criteria")
            return filtered_results

        except Exception as e:
            logger.error(f"Failed to search cases: {str(e)}")
            return []

    def _build_search_query(self, search_criteria: Dict[str, Any]) -> str:
        """Build search query from criteria."""
        query_parts = []

        # Add keywords
        if search_criteria.get('keywords'):
            query_parts.extend(search_criteria['keywords'])

        # Add subject matter
        if search_criteria.get('subject_matter'):
            query_parts.append(search_criteria['subject_matter'])

        # Add parties
        if search_criteria.get('parties'):
            query_parts.extend(search_criteria['parties'])

        # Add case type
        if search_criteria.get('case_type'):
            query_parts.append(search_criteria['case_type'])

        return " ".join(query_parts) if query_parts else "court cases"

    async def _perform_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform search on Kenya Law website."""
        if not self.driver:
            logger.error("Webdriver not available for search")
            return []

        try:
            # Navigate to search page
            search_url = f"{self.search_url}?q={query}"
            self.driver.get(search_url)

            # Wait for results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-results"))
            )

            # Extract search results
            results = []
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, ".search-result")

            for element in result_elements:
                try:
                    title_element = element.find_element(By.CSS_SELECTOR, ".case-title a")
                    title = title_element.text.strip()
                    url = title_element.get_attribute("href")

                    # Extract additional metadata
                    metadata = self._extract_search_result_metadata(element)

                    results.append({
                        "title": title,
                        "url": url,
                        "metadata": metadata
                    })

                except Exception as e:
                    logger.warning(f"Failed to extract result: {str(e)}")
                    continue

            return results

        except Exception as e:
            logger.error(f"Failed to perform search: {str(e)}")
            return []

    def _extract_search_result_metadata(self, element) -> Dict[str, Any]:
        """Extract metadata from search result element."""
        metadata = {}

        try:
            # Extract case number
            case_number_elem = element.find_element(By.CSS_SELECTOR, ".case-number")
            metadata["case_number"] = case_number_elem.text.strip()
        except:
            metadata["case_number"] = None

        try:
            # Extract court level
            court_elem = element.find_element(By.CSS_SELECTOR, ".court-level")
            metadata["court_level"] = court_elem.text.strip()
        except:
            metadata["court_level"] = None

        try:
            # Extract date
            date_elem = element.find_element(By.CSS_SELECTOR, ".case-date")
            metadata["date"] = date_elem.text.strip()
        except:
            metadata["date"] = None

        return metadata

    def _filter_search_results(self, results: List[Dict[str, Any]], criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter search results based on criteria."""
        filtered = []

        for result in results:
            # Check if result matches criteria
            if self._matches_criteria(result, criteria):
                filtered.append(result)

        return filtered

    def _matches_criteria(self, result: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if a result matches the search criteria."""
        # Basic matching logic - can be enhanced
        title_lower = result["title"].lower()

        # Check keywords
        if criteria.get('keywords'):
            for keyword in criteria['keywords']:
                if keyword.lower() not in title_lower:
                    return False

        # Check subject matter
        if criteria.get('subject_matter'):
            if criteria['subject_matter'].lower() not in title_lower:
                return False

        return True

    async def download_case(self, case_url: str) -> Optional[Case]:
        """
        Download and parse a complete case from Kenya Law.

        Args:
            case_url: URL of the case to download

        Returns:
            Case object with complete data, or None if failed
        """
        logger.info(f"Downloading case from: {case_url}")

        try:
            if not self.driver:
                logger.error("Webdriver not available for case download")
                return None

            # Navigate to case page
            self.driver.get(case_url)

            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "case-content"))
            )

            # Extract case data
            case_data = await self._extract_case_data()

            if case_data:
                logger.info(f"Successfully downloaded case: {case_data['metadata']['case_title']}")
                return case_data
            else:
                logger.warning(f"Failed to extract case data from: {case_url}")
                return None

        except Exception as e:
            logger.error(f"Failed to download case from {case_url}: {str(e)}")
            return None

    async def _extract_case_data(self) -> Optional[Case]:
        """Extract case data from the current page."""
        try:
            # Extract metadata
            metadata = self._extract_case_metadata()

            # Extract litigation hops
            litigation_hops = self._extract_litigation_hops()

            # Extract case content
            pleadings = self._extract_pleadings()
            decisions = self._extract_decisions()

            # Extract documents
            documents = self._extract_documents()

            # Create case object
            case = Case(
                metadata=metadata,
                litigation_hops=litigation_hops,
                pleadings=pleadings,
                decisions=decisions,
                documents=documents
            )

            return case

        except Exception as e:
            logger.error(f"Failed to extract case data: {str(e)}")
            return None

    def _extract_case_metadata(self) -> CaseMetadata:
        """Extract case metadata from the page."""
        try:
            # Extract case title
            title_elem = self.driver.find_element(By.CSS_SELECTOR, ".case-title")
            case_title = title_elem.text.strip()

            # Extract citation
            citation = None
            try:
                citation_elem = self.driver.find_element(By.CSS_SELECTOR, ".case-citation")
                citation = citation_elem.text.strip()
            except:
                pass

            # Extract parties
            parties = []
            try:
                parties_elem = self.driver.find_element(By.CSS_SELECTOR, ".case-parties")
                parties_text = parties_elem.text.strip()
                parties = [p.strip() for p in parties_text.split(" v ") if p.strip()]
            except:
                pass

            # Extract other metadata
            subject_matter = self._extract_text_by_selector(".subject-matter")
            case_type = self._extract_text_by_selector(".case-type")
            filing_date = self._extract_date_by_selector(".filing-date")

            return CaseMetadata(
                case_title=case_title,
                citation=citation,
                parties=parties,
                subject_matter=subject_matter,
                case_type=case_type,
                filing_date=filing_date,
                source_url=self.driver.current_url
            )

        except Exception as e:
            logger.error(f"Failed to extract case metadata: {str(e)}")
            raise

    def _extract_litigation_hops(self) -> List[LitigationHop]:
        """Extract litigation hops from the page."""
        hops = []

        try:
            # Look for litigation history section
            history_elements = self.driver.find_elements(By.CSS_SELECTOR, ".litigation-history .hop")

            for element in history_elements:
                try:
                    court_level_text = element.find_element(By.CSS_SELECTOR, ".court-level").text.strip()
                    court_level = self._map_court_level(court_level_text)

                    case_number = element.find_element(By.CSS_SELECTOR, ".case-number").text.strip()

                    status_text = element.find_element(By.CSS_SELECTOR, ".status").text.strip()
                    status = self._map_case_status(status_text)

                    outcome = self._extract_text_by_element(element, ".outcome")
                    judge = self._extract_text_by_element(element, ".judge")
                    court_location = self._extract_text_by_element(element, ".location")

                    hop = LitigationHop(
                        court_level=court_level,
                        case_number=case_number,
                        status=status,
                        outcome=outcome,
                        judge=judge,
                        court_location=court_location
                    )

                    hops.append(hop)

                except Exception as e:
                    logger.warning(f"Failed to extract litigation hop: {str(e)}")
                    continue

        except Exception as e:
            logger.warning(f"Failed to extract litigation hops: {str(e)}")

        return hops

    def _extract_pleadings(self) -> Optional[str]:
        """Extract case pleadings."""
        return self._extract_text_by_selector(".pleadings")

    def _extract_decisions(self) -> Optional[str]:
        """Extract court decisions."""
        return self._extract_text_by_selector(".decisions")

    def _extract_documents(self) -> Dict[str, str]:
        """Extract case documents."""
        documents = {}

        try:
            # Look for document links
            doc_elements = self.driver.find_elements(By.CSS_SELECTOR, ".case-documents a")

            for element in doc_elements:
                try:
                    doc_type = element.get_attribute("data-type") or "unknown"
                    doc_url = element.get_attribute("href")

                    if doc_url:
                        # Download document content
                        doc_content = self._download_document(doc_url)
                        if doc_content:
                            documents[doc_type] = doc_content

                except Exception as e:
                    logger.warning(f"Failed to extract document: {str(e)}")
                    continue

        except Exception as e:
            logger.warning(f"Failed to extract documents: {str(e)}")

        return documents

    def _download_document(self, doc_url: str) -> Optional[str]:
        """Download document content from URL."""
        try:
            # Use requests to download document
            import requests
            response = requests.get(doc_url, timeout=30)
            response.raise_for_status()

            # Parse content based on content type
            content_type = response.headers.get('content-type', '')

            if 'text/html' in content_type:
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup.get_text()
            elif 'text/plain' in content_type:
                return response.text
            else:
                # For PDFs and other formats, return a placeholder
                return f"[Document content not extracted - URL: {doc_url}]"

        except Exception as e:
            logger.warning(f"Failed to download document {doc_url}: {str(e)}")
            return None

    def _extract_text_by_selector(self, selector: str) -> Optional[str]:
        """Extract text by CSS selector."""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except:
            return None

    def _extract_text_by_element(self, element, selector: str) -> Optional[str]:
        """Extract text from element using selector."""
        try:
            sub_element = element.find_element(By.CSS_SELECTOR, selector)
            return sub_element.text.strip()
        except:
            return None

    def _extract_date_by_selector(self, selector: str) -> Optional[datetime]:
        """Extract date by CSS selector."""
        try:
            date_text = self._extract_text_by_selector(selector)
            if date_text:
                # Parse date - implement proper date parsing
                return datetime.now()  # Placeholder
        except:
            pass
        return None

    def _map_court_level(self, court_text: str) -> CourtLevel:
        """Map court text to CourtLevel enum."""
        court_lower = court_text.lower()

        if 'magistrate' in court_lower:
            return CourtLevel.MAGISTRATE
        elif 'high court' in court_lower:
            return CourtLevel.HIGH_COURT
        elif 'court of appeal' in court_lower or 'appeal' in court_lower:
            return CourtLevel.COURT_OF_APPEAL
        elif 'supreme court' in court_lower:
            return CourtLevel.SUPREME_COURT
        else:
            return CourtLevel.HIGH_COURT  # Default

    def _map_case_status(self, status_text: str) -> CaseStatus:
        """Map status text to CaseStatus enum."""
        status_lower = status_text.lower()

        if 'decided' in status_lower or 'judgment' in status_lower:
            return CaseStatus.DECIDED
        elif 'dismissed' in status_lower:
            return CaseStatus.DISMISSED
        elif 'settled' in status_lower:
            return CaseStatus.SETTLED
        elif 'appealed' in status_lower:
            return CaseStatus.APPEALED
        else:
            return CaseStatus.PENDING  # Default

    async def download_multiple_cases(self, case_urls: List[str]) -> List[Case]:
        """
        Download multiple cases concurrently.

        Args:
            case_urls: List of case URLs to download

        Returns:
            List of successfully downloaded cases
        """
        logger.info(f"Downloading {len(case_urls)} cases")

        tasks = [self.download_case(url) for url in case_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failed downloads
        successful_cases = []
        for result in results:
            if isinstance(result, Case):
                successful_cases.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Case download failed: {str(result)}")

        logger.info(f"Successfully downloaded {len(successful_cases)} out of {len(case_urls)} cases")
        return successful_cases

    def close(self) -> None:
        """Close the scraper and cleanup resources."""
        if self.driver:
            self.driver.quit()
            logger.info("Webdriver closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()