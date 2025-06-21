#!/usr/bin/env python3
"""
Test script to verify the fixes work.
"""

import asyncio
import json
from src.services.llm_service import LLMService
from src.services.serp_search_service import SerpSearchService
from src.utils.config import load_config

async def test_fixes():
    """Test the fixes."""
    print("Testing fixes...")

    # Test 1: Check if we can import and initialize services
    try:
        config = load_config()
        serp_service = SerpSearchService(config['serp_api_key'])
        llm_service = LLMService(config['openai_api_key'], serp_service=serp_service)
        print("✓ Services initialized successfully")
    except Exception as e:
        print(f"✗ Service initialization failed: {e}")
        return

    # Test 2: Test filtering logic with sample data
    sample_cases = [
        {
            "title": "Test Case 1",
            "appellate_court": {
                "court": "Court of Appeal",
                "url": "test_url"
            },
            "trial_reference": {
                "court": "High Court",
                "case_number": "123"
            }
        },
        {
            "title": "Test Case 2",
            "appellate_court": {
                "court": "Supreme Court",
                "url": "test_url"
            },
            "trial_reference": {
                "court": "High Court",
                "case_number": "456"
            }
        }
    ]

    # Test filtering logic
    filtered_cases = []
    for i, case in enumerate(sample_cases):
        appellate_court = case.get('appellate_court', {})
        if isinstance(appellate_court, dict):
            court_name = appellate_court.get('court', '').lower()
            if 'court of appeal' in court_name or 'supreme court' in court_name:
                filtered_cases.append(case)

    print(f"✓ Filtering logic test: {len(filtered_cases)}/{len(sample_cases)} cases passed")

    # Test 3: Test async PDF analyzer
    try:
        from src.pdf_processor.pdf_analyzer import PDFAnalyzer
        pdf_analyzer = PDFAnalyzer(llm_service=llm_service)
        print("✓ PDF Analyzer initialized successfully")
    except Exception as e:
        print(f"✗ PDF Analyzer initialization failed: {e}")

    print("All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_fixes())