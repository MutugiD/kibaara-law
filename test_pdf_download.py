#!/usr/bin/env python3
"""
Test script for PDF downloader functionality.

This script tests the PDF downloader to ensure it downloads actual PDFs
instead of HTML pages.
"""

import asyncio
import os
from typing import List, Dict, Any
from loguru import logger
from datetime import datetime

# Import services
from src.services.pdf_downloader import PDFDownloader


async def test_pdf_download() -> None:
    """Test PDF downloader with sample cases."""
    logger.info("=" * 80)
    logger.info("TESTING PDF DOWNLOADER")
    logger.info("=" * 80)

    # Initialize PDF downloader
    downloader = PDFDownloader(output_dir="data/raw")

    # Test cases from the filtering results
    test_cases = [
        {
            "title": "Civil Appeal 232 of 2016 - Nairobi",
            "appellate_court": {
                "court": "Court of Appeal",
                "case_number": "Civil Appeal 232 of 2016",
                "date": "Not specified",
                "url": "https://kenyalaw.org/caselaw/cases/view/194677/"
            },
            "trial_reference": {
                "court": "High Court",
                "case_number": "Not specified",
                "date": "Not specified"
            }
        },
        {
            "title": "Civil Appeal 12 of 2022",
            "appellate_court": {
                "court": "High Court",
                "case_number": "Civil Appeal 12 of 2022",
                "date": "Not specified",
                "url": "https://kenyalaw.org/caselaw/cases/view/282235/index.php?id=3479"
            },
            "trial_reference": {
                "court": "Magistrate's Court",
                "case_number": "Mutomo PMCC NO. E007 OF 2022",
                "date": "8th June 2022"
            }
        }
    ]

    logger.info(f"Testing PDF download for {len(test_cases)} cases")

    # Test individual case download
    for i, case in enumerate(test_cases, 1):
        logger.info(f"")
        logger.info(f"TESTING CASE {i}: {case['title']}")
        logger.info("-" * 60)

        try:
            # Download PDFs for this case
            result = await downloader.download_case_pdfs(case)

            if result['success']:
                logger.info(f"✓ SUCCESS: Downloaded {result['pdfs_downloaded']} PDFs")
                logger.info(f"  Case ID: {result['case_id']}")
                logger.info(f"  PDF links found: {result['pdf_links_found']}")
                logger.info(f"  PDFs downloaded: {result['pdfs_downloaded']}")

                # Show downloaded files
                for file_info in result['downloaded_files']:
                    logger.info(f"  - {file_info['filename']} ({file_info['size']} bytes)")
                    logger.info(f"    Type: {file_info['type']}")
                    logger.info(f"    URL: {file_info['url']}")

            else:
                logger.error(f"✗ FAILED: {result.get('error', 'Unknown error')}")

        except Exception as e:
            logger.error(f"✗ ERROR: {str(e)}")

    # Test multiple cases download
    logger.info(f"")
    logger.info("TESTING MULTIPLE CASES DOWNLOAD")
    logger.info("-" * 60)

    try:
        results = await downloader.download_multiple_cases(test_cases)

        successful_downloads = sum(1 for r in results if r['success'])
        total_pdfs = sum(r.get('pdfs_downloaded', 0) for r in results)

        logger.info(f"Multiple cases download completed:")
        logger.info(f"  Successful cases: {successful_downloads}/{len(test_cases)}")
        logger.info(f"  Total PDFs downloaded: {total_pdfs}")

        # Show summary for each case
        for i, result in enumerate(results, 1):
            status = "✓ SUCCESS" if result['success'] else "✗ FAILED"
            logger.info(f"  Case {i}: {status} - {result.get('pdfs_downloaded', 0)} PDFs")

    except Exception as e:
        logger.error(f"Error in multiple cases download: {str(e)}")

    logger.info("=" * 80)
    logger.info("PDF DOWNLOAD TEST COMPLETED")
    logger.info("=" * 80)


async def verify_downloaded_files() -> None:
    """Verify that downloaded files are actually PDFs."""
    logger.info("=" * 80)
    logger.info("VERIFYING DOWNLOADED FILES")
    logger.info("=" * 80)

    data_dir = "data/raw"
    if not os.path.exists(data_dir):
        logger.error("No data/raw directory found")
        return

    # List all files in the directory
    files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]
    logger.info(f"Found {len(files)} PDF files in {data_dir}")

    for i, filename in enumerate(files, 1):
        filepath = os.path.join(data_dir, filename)
        file_size = os.path.getsize(filepath)

        logger.info(f"")
        logger.info(f"FILE {i}: {filename}")
        logger.info(f"  Size: {file_size} bytes")
        logger.info(f"  Path: {filepath}")

        # Check if file is actually a PDF by reading first few bytes
        try:
            with open(filepath, 'rb') as f:
                header = f.read(4)
                if header == b'%PDF':
                    logger.info(f"  ✓ Valid PDF file")
                else:
                    logger.warning(f"  ⚠ Not a valid PDF file (header: {header})")
        except Exception as e:
            logger.error(f"  ✗ Error reading file: {str(e)}")

    logger.info("=" * 80)
    logger.info("FILE VERIFICATION COMPLETED")
    logger.info("=" * 80)


async def main() -> None:
    """Main test function."""
    try:
        await test_pdf_download()
        await verify_downloaded_files()
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())