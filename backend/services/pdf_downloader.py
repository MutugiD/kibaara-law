#!/usr/bin/env python3
"""
PDF Downloader Service

This service downloads actual PDF documents from Kenya Law URLs
instead of just the HTML pages.
"""

import asyncio
import os
import re
import hashlib
import aiohttp
import aiofiles
from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import urlparse, urljoin
from loguru import logger
from bs4 import BeautifulSoup


class PDFDownloader:
    """Downloads PDF documents from Kenya Law URLs."""

    def __init__(self, output_dir: str = "data/raw", max_retries: int = 3, session_timeout: int = 30, cache_service=None):
        """
        Initialize PDF downloader.

        Args:
            output_dir: Directory to save PDF files
            max_retries: Maximum number of retry attempts
            session_timeout: HTTP session timeout in seconds
            cache_service: Cache service for storing download status
        """
        self.output_dir = output_dir
        self.max_retries = max_retries
        self.session_timeout = session_timeout
        self.retry_delay = 2
        self.cache_service = cache_service

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Headers for different attempts
        self.headers_list = [
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
            {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Referer': 'https://kenyalaw.org/',
            },
            {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Referer': 'https://new.kenyalaw.org/',
            }
        ]

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe file system usage.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'\s+', '_', filename)
        filename = re.sub(r'[^\w\-_.]', '_', filename)

        # Limit length
        if len(filename) > 200:
            filename = filename[:200]

        return filename

    def _extract_case_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract case ID from Kenya Law URL.

        Args:
            url: Kenya Law URL

        Returns:
            Case ID if found, None otherwise
        """
        # Pattern for kenyalaw.org URLs
        kenyalaw_pattern = r'kenyalaw\.org/caselaw/cases/view/(\d+)'
        match = re.search(kenyalaw_pattern, url)
        if match:
            return match.group(1)

        # Pattern for new.kenyalaw.org URLs
        new_kenyalaw_pattern = r'new\.kenyalaw\.org/akn/ke/judgment/kehc/(\d+)/(\d+)'
        match = re.search(new_kenyalaw_pattern, url)
        if match:
            return f"{match.group(1)}_{match.group(2)}"

        return None

    def _extract_pdf_links_from_html(self, html_content: str, base_url: str) -> List[Dict[str, str]]:
        """
        Extract PDF download links from HTML content.

        Args:
            html_content: HTML content of the page
            base_url: Base URL for resolving relative links

        Returns:
            List of PDF link dictionaries with type and URL
        """
        pdf_links = []
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all PDF download links
        pdf_anchors = soup.find_all('a', href=re.compile(r'export.*pdf'))

        for anchor in pdf_anchors:
            href = anchor.get('href')
            if href:
                # Resolve relative URLs
                if href.startswith('/'):
                    pdf_url = urljoin(base_url, href)
                else:
                    pdf_url = href

                # Determine PDF type
                pdf_type = "standard"
                if "export_meta" in href:
                    pdf_type = "with_metadata"

                pdf_links.append({
                    'url': pdf_url,
                    'type': pdf_type,
                    'text': anchor.get_text(strip=True)
                })

        return pdf_links

    async def _download_pdf(self, pdf_url: str, filename: str, headers: Dict[str, str]) -> bool:
        """
        Download a single PDF file.

        Args:
            pdf_url: URL of the PDF to download
            filename: Filename to save the PDF as
            headers: HTTP headers to use

        Returns:
            True if download successful, False otherwise
        """
        filepath = os.path.join(self.output_dir, filename)

        try:
            timeout = aiohttp.ClientTimeout(total=self.session_timeout)
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(pdf_url) as response:
                    if response.status == 200:
                        # Check if response is actually a PDF
                        content_type = response.headers.get('content-type', '')
                        if 'pdf' not in content_type.lower() and 'application/octet-stream' not in content_type.lower():
                            logger.warning(f"Response is not a PDF: {content_type} for {pdf_url}")
                            return False

                        # Download the PDF
                        async with aiofiles.open(filepath, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                await f.write(chunk)

                        # Verify file was created and has content
                        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                            logger.info(f"Successfully downloaded PDF: {filename} ({os.path.getsize(filepath)} bytes)")
                            return True
                        else:
                            logger.error(f"Downloaded file is empty or missing: {filepath}")
                            return False
                    else:
                        logger.warning(f"HTTP {response.status} for PDF download: {pdf_url}")
                        return False

        except Exception as e:
            logger.error(f"Error downloading PDF {pdf_url}: {str(e)}")
            return False

    async def download_case_pdfs(self, case_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Download PDFs for a specific case.

        Args:
            case_info: Case information dictionary

        Returns:
            Download result dictionary
        """
        case_title = case_info.get('title', 'Unknown Case')
        appellate_url = case_info.get('appellate_court', {}).get('url', '')

        # Check cache first if cache service is available
        if self.cache_service:
            cache_key = f"pdf_download_{hashlib.md5(f'{case_title}:{appellate_url}'.encode()).hexdigest()}"
            cached_result = self.cache_service.get_case(cache_key)
            if cached_result and cached_result.get('success'):
                logger.info(f"Found cached PDF download for case: {case_title}")
                return cached_result

        logger.info(f"Downloading PDFs for case: {case_title}")

        if not appellate_url:
            logger.warning(f"No appellate URL found for case: {case_title}")
            return {
                'case_title': case_title,
                'success': False,
                'error': 'No appellate URL found',
                'pdfs_downloaded': 0,
                'pdf_files': []
            }

        # Download HTML page first
        html_content = await self._download_html_page(appellate_url)
        if not html_content:
            logger.error(f"Failed to download HTML page for case: {case_title}")
            return {
                'case_title': case_title,
                'success': False,
                'error': 'Failed to download HTML page',
                'pdfs_downloaded': 0,
                'pdf_files': []
            }

        # Extract PDF links from HTML
        pdf_links = self._extract_pdf_links_from_html(html_content, appellate_url)
        if not pdf_links:
            logger.warning(f"No PDF links found for case: {case_title}")
            return {
                'case_title': case_title,
                'success': False,
                'error': 'No PDF links found',
                'pdfs_downloaded': 0,
                'pdf_files': []
            }

        # Download PDFs
        downloaded_pdfs = []
        successful_downloads = 0

        for pdf_link in pdf_links:
            pdf_url = pdf_link['url']
            pdf_type = pdf_link['type']

            # Generate filename
            case_id = self._extract_case_id_from_url(appellate_url)
            if case_id:
                filename = f"{case_title}_{case_id}_{pdf_type}.pdf"
            else:
                filename = f"{case_title}_{pdf_type}.pdf"

            filename = self._sanitize_filename(filename)

            # Check if PDF already exists
            filepath = os.path.join(self.output_dir, filename)
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                logger.info(f"PDF already exists, skipping download: {filename}")
                downloaded_pdfs.append({
                    'filename': filename,
                    'filepath': filepath,
                    'type': pdf_type,
                    'url': pdf_url,
                    'size': os.path.getsize(filepath),
                    'cached': True
                })
                successful_downloads += 1
                continue

            # Download PDF
            success = False
            for attempt in range(self.max_retries):
                headers = self.headers_list[attempt % len(self.headers_list)]
                success = await self._download_pdf(pdf_url, filename, headers)

                if success:
                    downloaded_pdfs.append({
                        'filename': filename,
                        'filepath': filepath,
                        'type': pdf_type,
                        'url': pdf_url,
                        'size': os.path.getsize(filepath),
                        'cached': False
                    })
                    successful_downloads += 1
                    break
                else:
                    logger.warning(f"Download attempt {attempt + 1} failed for {filename}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)

        # Prepare result
        result = {
            'case_title': case_title,
            'success': successful_downloads > 0,
            'pdfs_downloaded': successful_downloads,
            'total_pdfs_found': len(pdf_links),
            'pdf_files': downloaded_pdfs,
            'appellate_url': appellate_url,
            'download_timestamp': datetime.now().isoformat()
        }

        # Cache the result if cache service is available
        if self.cache_service and result['success']:
            cache_key = f"pdf_download_{hashlib.md5(f'{case_title}:{appellate_url}'.encode()).hexdigest()}"
            self.cache_service.cache_case(cache_key, result)

        logger.info(f"Successfully downloaded {successful_downloads} PDFs for case: {case_title}")
        return result

    async def _download_html_page(self, url: str) -> Optional[str]:
        """
        Download HTML page to extract PDF links.

        Args:
            url: URL to download

        Returns:
            HTML content if successful, None otherwise
        """
        for attempt, headers in enumerate(self.headers_list):
            try:
                timeout = aiohttp.ClientTimeout(total=self.session_timeout)
                async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            content = await response.text()
                            logger.info(f"Downloaded HTML page: {len(content)} characters")
                            return content
                        else:
                            logger.warning(f"HTTP {response.status} for {url} (attempt {attempt + 1})")

            except Exception as e:
                logger.warning(f"Error downloading HTML {url} (attempt {attempt + 1}): {str(e)}")

            if attempt < len(self.headers_list) - 1:
                await asyncio.sleep(self.retry_delay * (attempt + 1))

        return None

    async def download_multiple_cases(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Download PDFs for multiple cases.

        Args:
            cases: List of case information dictionaries

        Returns:
            List of download results for each case
        """
        logger.info(f"Starting PDF download for {len(cases)} cases")

        results = []
        for i, case in enumerate(cases, 1):
            logger.info(f"Processing case {i}/{len(cases)}: {case.get('title', 'Unknown')}")
            result = await self.download_case_pdfs(case)
            results.append(result)

            # Small delay between cases to be respectful
            if i < len(cases):
                await asyncio.sleep(1)

        # Summary
        successful_downloads = sum(1 for r in results if r['success'])
        total_pdfs = sum(r.get('pdfs_downloaded', 0) for r in results)

        logger.info(f"PDF download completed: {successful_downloads}/{len(cases)} cases successful")
        logger.info(f"Total PDFs downloaded: {total_pdfs}")

        return results