#!/usr/bin/env python3
"""
Test script for document downloader functionality.

This script tests the improved document downloader with proper headers
and legal content extraction.
"""

import asyncio
import os
from typing import List, Dict, Any
from loguru import logger
from datetime import datetime

# Import services
from src.services.document_downloader import DocumentDownloader


async def test_document_download() -> None:
    """Test document downloader with problematic URLs."""
    logger.info("=" * 80)
    logger.info("TESTING DOCUMENT DOWNLOADER")
    logger.info("=" * 80)

    # Initialize document downloader
    downloader = DocumentDownloader()

    # Test URLs that previously failed with 403
    test_urls = [
        "https://new.kenyalaw.org/akn/ke/judgment/kehc/2023/3262/eng@2023-04-20",
        "https://new.kenyalaw.org/akn/ke/judgment/kehc/2024/16281/eng@2024-12-16",
        "https://kenyalaw.org/caselaw/cases/view/194677/",  # Working URL for comparison
    ]

    logger.info(f"Testing {len(test_urls)} URLs")

    for i, url in enumerate(test_urls, 1):
        logger.info(f"")
        logger.info(f"TESTING URL {i}: {url}")
        logger.info("-" * 60)

        try:
            # Download document
            result = await downloader.download_document(url)

            if result:
                logger.info(f"✓ SUCCESS: Downloaded {result['content_length']} characters")
                logger.info(f"  Filename: {result['filename']}")
                logger.info(f"  Title: {result['metadata'].get('title', 'Unknown')}")
                logger.info(f"  Court: {result['metadata'].get('court', 'Unknown')}")
                logger.info(f"  Case Number: {result['metadata'].get('case_number', 'Unknown')}")

                # Show legal content extraction
                legal_content = result.get('legal_content', {})
                logger.info(f"  Pleadings found: {len(legal_content.get('pleadings', []))}")
                logger.info(f"  Judgments found: {len(legal_content.get('judgments', []))}")
                logger.info(f"  Procedural steps: {len(legal_content.get('procedural_steps', []))}")
                logger.info(f"  Key legal phrases: {len(legal_content.get('key_legal_phrases', []))}")

                # Show sample pleadings
                pleadings = legal_content.get('pleadings', [])
                if pleadings:
                    logger.info(f"  Sample pleading: {pleadings[0][:100]}...")

            else:
                logger.error(f"✗ FAILED: Could not download document")

        except Exception as e:
            logger.error(f"✗ ERROR: {str(e)}")

    logger.info("=" * 80)
    logger.info("DOCUMENT DOWNLOAD TEST COMPLETED")
    logger.info("=" * 80)


async def test_legal_content_extraction() -> None:
    """Test legal content extraction from downloaded documents."""
    logger.info("=" * 80)
    logger.info("TESTING LEGAL CONTENT EXTRACTION")
    logger.info("=" * 80)

    # Check if we have downloaded documents
    download_dir = "downloads"
    if not os.path.exists(download_dir):
        logger.error("No downloads directory found")
        return

    # List downloaded files
    files = [f for f in os.listdir(download_dir) if f.endswith('.html')]
    logger.info(f"Found {len(files)} downloaded documents")

    downloader = DocumentDownloader()

    for i, filename in enumerate(files[:3], 1):  # Test first 3 files
        filepath = os.path.join(download_dir, filename)
        logger.info(f"")
        logger.info(f"ANALYZING FILE {i}: {filename}")
        logger.info("-" * 60)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract legal content
            legal_content = downloader._extract_legal_content(content)

            logger.info(f"Content length: {len(content)} characters")
            logger.info(f"Pleadings found: {len(legal_content.get('pleadings', []))}")
            logger.info(f"Judgments found: {len(legal_content.get('judgments', []))}")
            logger.info(f"Procedural steps: {len(legal_content.get('procedural_steps', []))}")
            logger.info(f"Key legal phrases: {legal_content.get('key_legal_phrases', [])}")

            # Show sample content
            pleadings = legal_content.get('pleadings', [])
            if pleadings:
                logger.info(f"Sample pleading: {pleadings[0][:150]}...")

            judgments = legal_content.get('judgments', [])
            if judgments:
                logger.info(f"Sample judgment: {judgments[0][:150]}...")

        except Exception as e:
            logger.error(f"Error analyzing {filename}: {str(e)}")

    logger.info("=" * 80)
    logger.info("LEGAL CONTENT EXTRACTION TEST COMPLETED")
    logger.info("=" * 80)


async def main() -> None:
    """Main test function."""
    try:
        await test_document_download()
        await test_legal_content_extraction()
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())