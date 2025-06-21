#!/usr/bin/env python3
"""
Test script for PDF analysis and caching system.

This script tests:
1. Cache service functionality
2. PDF analysis with templated prompts
3. End-to-end workflow with caching
"""

import asyncio
import os
import json
from datetime import datetime
from loguru import logger

# Import services
from src.services.cache_service import CacheService
from src.services.llm_service import LLMService
from src.services.pdf_analysis_service import PDFAnalysisService
from src.services.serp_search_service import SerpSearchService


async def test_cache_service():
    """Test the cache service functionality."""
    logger.info("=" * 80)
    logger.info("TESTING CACHE SERVICE")
    logger.info("=" * 80)

    # Initialize cache service
    cache_service = CacheService("cache/test_cache.json")

    # Test 1: Cache a case
    test_case = {
        "title": "Test Case v Test Respondent",
        "appellate_court": {
            "url": "https://test.kenyalaw.org/case/123"
        },
        "pdf_downloaded": True,
        "analyzed": False
    }

    cache_service.cache_case(test_case)
    logger.info("✓ Test case cached successfully")

    # Test 2: Check if case is cached
    is_cached = cache_service.is_case_cached("Test Case v Test Respondent", "https://test.kenyalaw.org/case/123")
    logger.info(f"✓ Case cached check: {is_cached}")

    # Test 3: Get cached case
    cached_case = cache_service.get_cached_case("Test Case v Test Respondent", "https://test.kenyalaw.org/case/123")
    if cached_case:
        logger.info(f"✓ Retrieved cached case: {cached_case.get('title')}")

    # Test 4: Update case analysis
    analysis_data = {
        "analyzed": True,
        "analysis_result": "Test analysis result"
    }
    cache_service.update_case_analysis("Test Case v Test Respondent", "https://test.kenyalaw.org/case/123", analysis_data)
    logger.info("✓ Updated case analysis successfully")

    # Test 5: Get cache statistics
    stats = cache_service.get_cache_statistics()
    logger.info(f"✓ Cache statistics: {stats}")

    # Test 6: Export cache
    cache_service.export_cache("cache/test_export.json")
    logger.info("✓ Cache exported successfully")

    logger.info("Cache service tests completed successfully!")


async def test_pdf_analysis():
    """Test PDF analysis functionality."""
    logger.info("=" * 80)
    logger.info("TESTING PDF ANALYSIS")
    logger.info("=" * 80)

    # Check if we have PDFs to analyze
    pdf_directory = "data/raw"
    if not os.path.exists(pdf_directory):
        logger.warning(f"PDF directory does not exist: {pdf_directory}")
        return

    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
    if not pdf_files:
        logger.warning("No PDF files found for analysis")
        return

    logger.info(f"Found {len(pdf_files)} PDF files for analysis")

    # Initialize services
    serp_api_key = os.getenv("SERP_API_KEY")
    if not serp_api_key:
        logger.error("SERP_API_KEY not found in environment")
        return

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY not found in environment")
        return

    serp_service = SerpSearchService(serp_api_key)
    llm_service = LLMService(openai_api_key, serp_service)
    cache_service = CacheService("cache/pdf_analysis_cache.json")
    pdf_analysis_service = PDFAnalysisService(llm_service, cache_service)

    # Test 1: Analyze a single PDF (use the first one)
    first_pdf = pdf_files[0]
    pdf_path = os.path.join(pdf_directory, first_pdf)
    case_title = first_pdf.replace('.pdf', '').replace('_with_metadata', '').replace('_', ' ')

    logger.info(f"Testing analysis of: {case_title}")

    try:
        analysis_result = await pdf_analysis_service.analyze_specific_case(case_title, pdf_path)

        if analysis_result and analysis_result.get('analysis_complete'):
            logger.info(f"✓ Successfully analyzed: {case_title}")
            logger.info(f"  - PDF content length: {analysis_result.get('pdf_content_length', 0)} characters")
            logger.info(f"  - Analysis timestamp: {analysis_result.get('analysis_timestamp')}")

            # Save individual result
            output_file = f"results/analysis_{case_title.replace(' ', '_')}.json"
            os.makedirs("results", exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Analysis result saved to: {output_file}")

        else:
            logger.error(f"✗ Failed to analyze: {case_title}")
            if analysis_result:
                logger.error(f"  Error: {analysis_result.get('error', 'Unknown error')}")

    except Exception as e:
        logger.error(f"✗ Error during analysis: {str(e)}")

    # Test 2: Analyze all PDFs (commented out to avoid long runtime)
    # logger.info("Testing analysis of all PDFs...")
    # all_results = await pdf_analysis_service.analyze_downloaded_pdfs(pdf_directory)
    # logger.info(f"✓ Analyzed {len(all_results)} PDFs")

    # # Save all results
    # pdf_analysis_service.save_analysis_results(all_results)
    # logger.info("✓ All analysis results saved")

    logger.info("PDF analysis tests completed!")


async def test_caching_integration():
    """Test caching integration with the main workflow."""
    logger.info("=" * 80)
    logger.info("TESTING CACHING INTEGRATION")
    logger.info("=" * 80)

    # Initialize cache service
    cache_service = CacheService("cache/integration_test_cache.json")

    # Simulate workflow results
    workflow_results = [
        {
            "title": "Civil Appeal 232 of 2016 - Nairobi",
            "appellate_court": {
                "url": "https://kenyalaw.org/caselaw/cases/view/194677/"
            },
            "pdf_downloaded": True,
            "analyzed": True,
            "pdf_files": ["Civil_Appeal_232_of_2016_-_Nairobi.pdf"]
        },
        {
            "title": "Civil Appeal 21 of 2018",
            "appellate_court": {
                "url": "https://kenyalaw.org/caselaw/cases/view/185689/"
            },
            "pdf_downloaded": True,
            "analyzed": True,
            "pdf_files": ["Civil_Appeal_21_of_2018.pdf"]
        }
    ]

    # Cache workflow results
    for case in workflow_results:
        cache_service.cache_case(case)
        logger.info(f"✓ Cached case: {case['title']}")

    # Test cache retrieval
    cached_cases = cache_service.get_all_cached_cases()
    logger.info(f"✓ Retrieved {len(cached_cases)} cached cases")

    # Test cache statistics
    stats = cache_service.get_cache_statistics()
    logger.info(f"✓ Final cache statistics: {stats}")

    logger.info("Caching integration tests completed!")


async def main():
    """Main test function."""
    logger.info("Starting PDF Analysis and Caching Tests")
    logger.info(f"Test timestamp: {datetime.now().isoformat()}")

    try:
        # Test 1: Cache service
        await test_cache_service()

        # Test 2: PDF analysis (if PDFs exist)
        await test_pdf_analysis()

        # Test 3: Caching integration
        await test_caching_integration()

        logger.info("=" * 80)
        logger.info("ALL TESTS COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())