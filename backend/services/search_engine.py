"""
Search engine service for coordinating legal case searches.

This module coordinates between prompt processing and Kenya Law scraping
to find relevant cases based on user requirements.
"""

import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger

from ..models.prompt_models import Prompt, SearchCriteria
from ..models.result_models import SearchResult
from .kenya_law_scraper import KenyaLawScraper


class SearchEngine:
    """
    Service for coordinating legal case searches.

    This service acts as the main coordinator between prompt processing
    and Kenya Law scraping to find relevant cases.
    """

    def __init__(self) -> None:
        """Initialize the search engine."""
        self.scraper = KenyaLawScraper()
        self.max_search_results = 100
        self.min_relevance_score = 0.3

    async def search_cases(self, prompt: Prompt) -> List[SearchResult]:
        """
        Search for cases based on a processed prompt.

        Args:
            prompt: The processed user prompt with search criteria

        Returns:
            List of search results with relevance scoring
        """
        logger.info(f"Searching for cases based on prompt: {prompt.text[:100]}...")

        try:
            # Convert search criteria to dictionary format
            search_criteria = self._convert_criteria_to_dict(prompt.search_criteria)

            # Perform search using scraper
            raw_results = await self.scraper.search_cases(search_criteria)

            # Convert to SearchResult objects and score relevance
            search_results = []
            for raw_result in raw_results:
                relevance_score = self._calculate_relevance_score(raw_result, prompt.search_criteria)

                if relevance_score >= self.min_relevance_score:
                    search_result = SearchResult(
                        case_url=raw_result["url"],
                        case_title=raw_result["title"],
                        case_number=raw_result.get("metadata", {}).get("case_number"),
                        court_level=raw_result.get("metadata", {}).get("court_level"),
                        relevance_score=relevance_score,
                        match_reasons=self._get_match_reasons(raw_result, prompt.search_criteria),
                        metadata=raw_result.get("metadata", {})
                    )
                    search_results.append(search_result)

            # Sort by relevance score
            search_results.sort(key=lambda x: x.relevance_score, reverse=True)

            # Limit results based on prompt requirements
            max_results = min(prompt.search_criteria.case_count * 2, self.max_search_results)
            search_results = search_results[:max_results]

            logger.info(f"Found {len(search_results)} relevant cases")
            return search_results

        except Exception as e:
            logger.error(f"Failed to search cases: {str(e)}")
            return []

    def _convert_criteria_to_dict(self, criteria: SearchCriteria) -> Dict[str, Any]:
        """Convert SearchCriteria to dictionary format for scraper."""
        return {
            "case_count": criteria.case_count,
            "court_levels": [level.value for level in criteria.court_levels],
            "date_from": criteria.date_from,
            "date_to": criteria.date_to,
            "subject_matter": criteria.subject_matter,
            "case_type": criteria.case_type,
            "parties": criteria.parties,
            "keywords": criteria.keywords,
            "require_multi_hop": criteria.require_multi_hop,
            "min_hops": criteria.min_hops
        }

    def _calculate_relevance_score(self, result: Dict[str, Any], criteria: SearchCriteria) -> float:
        """
        Calculate relevance score for a search result.

        Args:
            result: Raw search result from scraper
            criteria: Search criteria from prompt

        Returns:
            Relevance score between 0 and 1
        """
        score = 0.0
        title_lower = result["title"].lower()

        # Score based on keywords
        if criteria.keywords:
            keyword_matches = sum(1 for keyword in criteria.keywords if keyword.lower() in title_lower)
            keyword_score = keyword_matches / len(criteria.keywords)
            score += keyword_score * 0.4

        # Score based on subject matter
        if criteria.subject_matter:
            subject_lower = criteria.subject_matter.lower()
            if subject_lower in title_lower:
                score += 0.3

        # Score based on case type
        if criteria.case_type:
            case_type_lower = criteria.case_type.lower()
            if case_type_lower in title_lower:
                score += 0.2

        # Score based on parties
        if criteria.parties:
            party_matches = sum(1 for party in criteria.parties if party.lower() in title_lower)
            party_score = party_matches / len(criteria.parties)
            score += party_score * 0.1

        # Bonus for multi-hop indicators
        multi_hop_indicators = ["appeal", "appellate", "supreme", "magistrate", "high court"]
        if any(indicator in title_lower for indicator in multi_hop_indicators):
            score += 0.1

        return min(score, 1.0)

    def _get_match_reasons(self, result: Dict[str, Any], criteria: SearchCriteria) -> List[str]:
        """Get reasons why a result matches the search criteria."""
        reasons = []
        title_lower = result["title"].lower()

        # Check keywords
        if criteria.keywords:
            matched_keywords = [kw for kw in criteria.keywords if kw.lower() in title_lower]
            if matched_keywords:
                reasons.append(f"Matches keywords: {', '.join(matched_keywords)}")

        # Check subject matter
        if criteria.subject_matter and criteria.subject_matter.lower() in title_lower:
            reasons.append(f"Matches subject matter: {criteria.subject_matter}")

        # Check case type
        if criteria.case_type and criteria.case_type.lower() in title_lower:
            reasons.append(f"Matches case type: {criteria.case_type}")

        # Check parties
        if criteria.parties:
            matched_parties = [party for party in criteria.parties if party.lower() in title_lower]
            if matched_parties:
                reasons.append(f"Matches parties: {', '.join(matched_parties)}")

        # Check multi-hop indicators
        multi_hop_indicators = ["appeal", "appellate", "supreme", "magistrate", "high court"]
        found_indicators = [ind for ind in multi_hop_indicators if ind in title_lower]
        if found_indicators:
            reasons.append(f"Multi-hop indicators: {', '.join(found_indicators)}")

        return reasons

    async def get_case_urls_for_analysis(self, search_results: List[SearchResult], max_cases: int) -> List[str]:
        """
        Get case URLs for detailed analysis.

        Args:
            search_results: List of search results
            max_cases: Maximum number of cases to analyze

        Returns:
            List of case URLs to download and analyze
        """
        # Filter for high relevance results
        high_relevance = [r for r in search_results if r.relevance_score >= 0.6]

        # If we have enough high relevance results, use those
        if len(high_relevance) >= max_cases:
            return [r.case_url for r in high_relevance[:max_cases]]

        # Otherwise, use top results regardless of score
        return [r.case_url for r in search_results[:max_cases]]

    async def close(self) -> None:
        """Close the search engine and cleanup resources."""
        if self.scraper:
            self.scraper.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        asyncio.create_task(self.close())