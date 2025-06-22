"""
Serp search service for live web searches of Kenyan court cases.

This module handles live web searches using Serp API to find
Kenyan court cases with 2-hop litigation processes.
"""

import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime
import json


class SerpSearchService:
    """
    Service for performing live web searches using Serp API.

    This service searches for Kenyan court cases with 2-hop litigation
    and provides structured results for further processing.
    """

    def __init__(self, api_key: str) -> None:
        """
        Initialize the Serp search service.

        Args:
            api_key: Serp API key
        """
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
        self.session_timeout = 30
        self.max_retries = 3
        self.retry_delay = 1.0

    async def search_kenyan_cases(self, search_query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for Kenyan court cases using Serp API.

        Args:
            search_query: The search query for finding cases
            max_results: Maximum number of results to return

        Returns:
            List of case information dictionaries
        """
        logger.info("=" * 80)
        logger.info("STARTING SERP API SEARCH FOR KENYAN COURT CASES")
        logger.info("=" * 80)
        logger.info(f"Search Query: {search_query}")
        logger.info(f"Target Results: {max_results} cases")
        logger.info(f"Search Timestamp: {datetime.now().isoformat()}")
        logger.info("-" * 80)

        try:
            # Perform multiple targeted searches
            search_results = []

            # Search 1: Kenya Law website for appellate cases specifically
            kenya_law_results = await self._search_kenya_law_appellate(search_query, max_results)
            search_results.extend(kenya_law_results)

            # Search 2: General web search for Kenyan appellate cases
            web_results = await self._search_web_appellate(search_query, max_results)
            search_results.extend(web_results)

            # Search 3: Specific search for Court of Appeal cases
            appeal_results = await self._search_appeal_cases(search_query, max_results)
            search_results.extend(appeal_results)

            # Search 4: Search for 2-hop litigation patterns
            two_hop_results = await self._search_two_hop_patterns(search_query, max_results)
            search_results.extend(two_hop_results)

            # Filter and deduplicate results
            filtered_results = self._filter_and_deduplicate(search_results, max_results)

            # Log search results
            logger.info("-" * 80)
            logger.info("SERP SEARCH RESULTS SUMMARY")
            logger.info("-" * 80)
            logger.info(f"Total raw results found: {len(search_results)}")
            logger.info(f"Filtered results: {len(filtered_results)}")

            if filtered_results:
                logger.info("DETAILED SEARCH RESULTS:")
                for i, result in enumerate(filtered_results, 1):
                    logger.info(f"")
                    logger.info(f"RESULT {i}:")
                    logger.info(f"  Title: {result.get('title', 'Unknown')}")
                    logger.info(f"  URL: {result.get('url', 'Unknown')}")
                    logger.info(f"  Snippet: {result.get('snippet', 'Unknown')[:200]}...")
                    logger.info(f"  Source: {result.get('source', 'Unknown')}")
                    logger.info("  " + "-" * 60)

            logger.info("=" * 80)
            logger.info("SERP SEARCH COMPLETED")
            logger.info("=" * 80)

            return filtered_results

        except Exception as e:
            logger.error(f"Failed to search Kenyan cases with Serp: {str(e)}")
            logger.error("=" * 80)
            return []

    async def _search_kenya_law_appellate(self, search_query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search Kenya Law website specifically for appellate cases."""
        logger.info("Searching Kenya Law website for appellate cases...")

        try:
            params = {
                "api_key": self.api_key,
                "engine": "google",
                "q": f"site:kenyalaw.org appellate court appeal judgment 2-hop litigation",
                "num": max_results,
                "gl": "ke",  # Kenya
                "hl": "en"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("organic_results", [])

                        formatted_results = []
                        for result in results:
                            formatted_results.append({
                                "title": result.get("title", ""),
                                "url": result.get("link", ""),
                                "snippet": result.get("snippet", ""),
                                "source": "Kenya Law Appellate",
                                "search_type": "kenya_law_appellate"
                            })

                        logger.info(f"Found {len(formatted_results)} results from Kenya Law appellate search")
                        return formatted_results
                    else:
                        logger.error(f"Kenya Law appellate search failed with status {response.status}")
                        return []

        except Exception as e:
            logger.error(f"Kenya Law appellate search error: {str(e)}")
            return []

    async def _search_web_appellate(self, search_query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search general web for Kenyan appellate court cases."""
        logger.info("Searching general web for Kenyan appellate court cases...")

        try:
            params = {
                "api_key": self.api_key,
                "engine": "google",
                "q": f"Kenya appellate court cases appeal judgment 2-hop litigation trial court",
                "num": max_results,
                "gl": "ke",  # Kenya
                "hl": "en"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("organic_results", [])

                        formatted_results = []
                        for result in results:
                            formatted_results.append({
                                "title": result.get("title", ""),
                                "url": result.get("link", ""),
                                "snippet": result.get("snippet", ""),
                                "source": "Web Appellate Search",
                                "search_type": "web_appellate"
                            })

                        logger.info(f"Found {len(formatted_results)} results from web appellate search")
                        return formatted_results
                    else:
                        logger.error(f"Web appellate search failed with status {response.status}")
                        return []

        except Exception as e:
            logger.error(f"Web appellate search error: {str(e)}")
            return []

    async def _search_appeal_cases(self, search_query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search specifically for Court of Appeal cases."""
        logger.info("Searching for Court of Appeal cases...")

        try:
            params = {
                "api_key": self.api_key,
                "engine": "google",
                "q": f"Kenya Court of Appeal cases 2-hop litigation trial appellate",
                "num": max_results,
                "gl": "ke",  # Kenya
                "hl": "en"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("organic_results", [])

                        formatted_results = []
                        for result in results:
                            formatted_results.append({
                                "title": result.get("title", ""),
                                "url": result.get("link", ""),
                                "snippet": result.get("snippet", ""),
                                "source": "Appeal Search",
                                "search_type": "appeal"
                            })

                        logger.info(f"Found {len(formatted_results)} results from appeal search")
                        return formatted_results
                    else:
                        logger.error(f"Appeal search failed with status {response.status}")
                        return []

        except Exception as e:
            logger.error(f"Appeal search error: {str(e)}")
            return []

    async def _search_two_hop_patterns(self, search_query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search specifically for 2-hop litigation patterns."""
        logger.info("Searching for 2-hop litigation patterns...")

        try:
            params = {
                "api_key": self.api_key,
                "engine": "google",
                "q": f"Kenya court cases trial appellate 2-hop litigation progression",
                "num": max_results,
                "gl": "ke",  # Kenya
                "hl": "en"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("organic_results", [])

                        formatted_results = []
                        for result in results:
                            formatted_results.append({
                                "title": result.get("title", ""),
                                "url": result.get("link", ""),
                                "snippet": result.get("snippet", ""),
                                "source": "2-Hop Pattern Search",
                                "search_type": "two_hop_patterns"
                            })

                        logger.info(f"Found {len(formatted_results)} results from 2-hop pattern search")
                        return formatted_results
                    else:
                        logger.error(f"2-hop pattern search failed with status {response.status}")
                        return []

        except Exception as e:
            logger.error(f"2-hop pattern search error: {str(e)}")
            return []

    def _filter_and_deduplicate(self, results: List[Dict[str, Any]], max_results: int) -> List[Dict[str, Any]]:
        """Filter and deduplicate search results."""
        logger.info("Filtering and deduplicating search results...")

        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []

        for result in results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)

        # Filter for relevant results (Kenya Law, court cases, etc.)
        filtered_results = []
        keywords = ["kenyalaw", "court", "appeal", "trial", "judgment", "eKLR"]

        for result in unique_results:
            title = result.get("title", "").lower()
            snippet = result.get("snippet", "").lower()
            url = result.get("url", "").lower()

            # Check if result contains relevant keywords
            if any(keyword in title or keyword in snippet or keyword in url for keyword in keywords):
                filtered_results.append(result)

        # Limit to max_results
        final_results = filtered_results[:max_results]

        logger.info(f"Filtered {len(results)} results to {len(final_results)} unique, relevant results")
        return final_results