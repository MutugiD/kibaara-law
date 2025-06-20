#!/usr/bin/env python3
"""
Test script for Serp integration and workflow validation.

This script tests the Serp search service and LLM integration
step by step to ensure the workflow is working correctly.
"""

import asyncio
import os
from typing import List, Dict, Any
from loguru import logger
from datetime import datetime

# Import services
from src.services.serp_search_service import SerpSearchService
from src.services.llm_service import LLMService


async def test_serp_search() -> None:
    """Test Serp search service directly."""
    logger.info("=" * 80)
    logger.info("TESTING SERP SEARCH SERVICE")
    logger.info("=" * 80)

    # Initialize Serp service
    serp_api_key = "9bdae94fbdaf866f40cdcfa38607ba9300a359530b2c656e2d6fcea3501ca9e1"
    serp_service = SerpSearchService(serp_api_key)

    # Test search
    search_query = "Kenya Court of Appeal cases 2-hop litigation trial appellate"
    results = await serp_service.search_kenyan_cases(search_query, max_results=5)

    logger.info(f"Serp search returned {len(results)} results")

    if results:
        logger.info("SERP SEARCH RESULTS:")
        for i, result in enumerate(results, 1):
            logger.info(f"")
            logger.info(f"Result {i}:")
            logger.info(f"  Title: {result.get('title', 'Unknown')}")
            logger.info(f"  URL: {result.get('url', 'Unknown')}")
            logger.info(f"  Source: {result.get('source', 'Unknown')}")
            logger.info("  " + "-" * 60)

    return results


async def test_llm_serp_integration() -> None:
    """Test LLM service with Serp integration."""
    logger.info("=" * 80)
    logger.info("TESTING LLM + SERP INTEGRATION")
    logger.info("=" * 80)

    # Initialize services
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY not found in environment")
        return

    serp_api_key = "9bdae94fbdaf866f40cdcfa38607ba9300a359530b2c656e2d6fcea3501ca9e1"
    serp_service = SerpSearchService(serp_api_key)
    llm_service = LLMService(openai_api_key, serp_service)

    # Test integrated search
    search_query = "Kenya Court of Appeal cases 2-hop litigation trial appellate"
    cases = await llm_service.search_kenyan_cases_with_serp(search_query, max_results=3)

    logger.info(f"LLM + Serp integration returned {len(cases)} cases")

    if cases:
        logger.info("INTEGRATED SEARCH RESULTS:")
        for i, case in enumerate(cases, 1):
            logger.info(f"")
            logger.info(f"Case {i}:")
            logger.info(f"  Title: {case.get('title', 'Unknown')}")
            logger.info(f"  Trial Court: {case.get('trial_court', {}).get('court', 'Unknown')}")
            logger.info(f"  Appellate Court: {case.get('appellate_court', {}).get('court', 'Unknown')}")
            logger.info(f"  Trial URL: {case.get('trial_court', {}).get('url', 'Unknown')}")
            logger.info(f"  Appellate URL: {case.get('appellate_court', {}).get('url', 'Unknown')}")
            logger.info(f"  Confidence: {case.get('confidence', 'Unknown')}")
            logger.info("  " + "-" * 60)

    return cases


async def test_full_workflow() -> None:
    """Test the complete workflow step by step."""
    logger.info("=" * 80)
    logger.info("TESTING FULL WORKFLOW")
    logger.info("=" * 80)

    # Step 1: Test Serp search
    logger.info("STEP 1: Testing Serp search...")
    serp_results = await test_serp_search()

    if not serp_results:
        logger.error("Serp search failed - stopping workflow test")
        return

    # Step 2: Test LLM + Serp integration
    logger.info("STEP 2: Testing LLM + Serp integration...")
    llm_results = await test_llm_serp_integration()

    if not llm_results:
        logger.error("LLM + Serp integration failed - stopping workflow test")
        return

    # Step 3: Validate results
    logger.info("STEP 3: Validating results...")
    valid_cases = 0
    for case in llm_results:
        trial_court = case.get('trial_court', {})
        appellate_court = case.get('appellate_court', {})

        if (trial_court.get('court') and appellate_court.get('court') and
            trial_court.get('url') and appellate_court.get('url')):
            valid_cases += 1

    logger.info(f"Valid cases with 2-hop litigation: {valid_cases}/{len(llm_results)}")

    logger.info("=" * 80)
    logger.info("WORKFLOW TEST COMPLETED")
    logger.info("=" * 80)


async def main() -> None:
    """Main test function."""
    try:
        await test_full_workflow()
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())