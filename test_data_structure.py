#!/usr/bin/env python3
"""
Test script to check the actual structure of LLM service response.
"""

import asyncio
import json
from src.services.llm_service import LLMService
from src.services.serp_search_service import SerpSearchService
from src.utils.config import load_config

async def test_llm_structure():
    """Test the LLM service to see the actual data structure."""
    config = load_config()

    # Initialize services
    serp_service = SerpSearchService(config['serp_api_key'])
    llm_service = LLMService(config['openai_api_key'], serp_service=serp_service)

    # Test the search
    prompt_text = "Find Kenyan court cases with 2-hop litigation processes"
    cases = await llm_service.search_kenyan_cases_with_serp(prompt_text, max_results=3)

    print(f"Found {len(cases)} cases")
    print("\n" + "="*80)
    print("ACTUAL DATA STRUCTURE:")
    print("="*80)

    for i, case in enumerate(cases, 1):
        print(f"\nCASE {i}:")
        print(f"Title: {case.get('title', 'Unknown')}")
        print(f"Trial Court: {case.get('trial_court', {})}")
        print(f"Appellate Court: {case.get('appellate_court', {})}")
        print(f"Full case structure:")
        print(json.dumps(case, indent=2, default=str))
        print("-" * 60)

if __name__ == "__main__":
    asyncio.run(test_llm_structure())