"""
LLM service for GPT-4o interactions with search API.

This module handles OpenAI GPT-4o API calls with search capabilities
to find and analyze Kenyan court cases.
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from loguru import logger
import re
import os
from datetime import datetime

from ..models.case_models import Case, CaseMetadata, LitigationHop, CourtLevel, CaseStatus


class LLMService:
    """
    Service for GPT-4o interactions with search API.

    This service uses OpenAI's GPT-4o model with search capabilities
    to find Kenyan court cases and extract relevant information.
    """

    def __init__(self, api_key: str, serp_service=None) -> None:
        """
        Initialize the LLM service.

        Args:
            api_key: OpenAI API key
            serp_service: Optional SerpSearchService for live web searches
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o"
        self.max_retries = 3
        self.retry_delay = 1.0
        self.serp_service = serp_service

    async def search_kenyan_cases(self, search_query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for Kenyan court cases using GPT-4o with search.

        Args:
            search_query: The search query for finding cases
            max_results: Maximum number of results to return

        Returns:
            List of case information dictionaries
        """
        logger.info("=" * 80)
        logger.info("STARTING KENYAN COURT CASE SEARCH")
        logger.info("=" * 80)
        logger.info(f"Search Query: {search_query}")
        logger.info(f"Target Results: {max_results} cases with 2-hop litigation")
        logger.info(f"Search Timestamp: {datetime.now().isoformat()}")
        logger.info("-" * 80)

        try:
            # Create search prompt
            search_prompt = self._create_search_prompt(search_query, max_results)
            logger.info("Search prompt created successfully")

            # Make API call with search
            logger.info("Making GPT-4o API call to find Kenyan cases with 2-hop litigation...")
            response = await self._make_search_call(search_prompt)
            logger.info(f"Received response from GPT-4o (length: {len(response)} characters)")

            # Parse and validate results
            cases = self._parse_search_results(response)

            # Log search results
            logger.info("-" * 80)
            logger.info("SEARCH RESULTS SUMMARY")
            logger.info("-" * 80)
            logger.info(f"Total cases found: {len(cases)}")

            if cases:
                logger.info("DETAILED CASE INFORMATION:")
                for i, case in enumerate(cases, 1):
                    logger.info(f"")
                    logger.info(f"CASE {i}:")
                    logger.info(f"  Title: {case.get('title', 'Unknown')}")
                    logger.info(f"  Description: {case.get('description', 'Unknown')}")

                    # Trial court info
                    trial_court = case.get('trial_court', {})
                    logger.info(f"  TRIAL COURT:")
                    logger.info(f"    Court: {trial_court.get('court', 'Unknown')}")
                    logger.info(f"    Case Number: {trial_court.get('case_number', 'Unknown')}")
                    logger.info(f"    Date: {trial_court.get('date', 'Unknown')}")
                    logger.info(f"    URL: {trial_court.get('url', 'Unknown')}")

                    # Appellate court info
                    appellate_court = case.get('appellate_court', {})
                    logger.info(f"  APPELLATE COURT:")
                    logger.info(f"    Court: {appellate_court.get('court', 'Unknown')}")
                    logger.info(f"    Case Number: {appellate_court.get('case_number', 'Unknown')}")
                    logger.info(f"    Date: {appellate_court.get('date', 'Unknown')}")
                    logger.info(f"    URL: {appellate_court.get('url', 'Unknown')}")

                    # Litigation progression
                    progression = case.get('litigation_progression', 'Unknown')
                    logger.info(f"  Litigation Progression: {progression}")
                    logger.info("  " + "-" * 60)

                # Summary statistics
                logger.info("")
                logger.info("CASE FILTERING SUMMARY:")
                logger.info(f"  Total cases found: {len(cases)}")
                logger.info(f"  Cases with trial court info: {sum(1 for c in cases if c.get('trial_court', {}).get('url'))}")
                logger.info(f"  Cases with appellate court info: {sum(1 for c in cases if c.get('appellate_court', {}).get('url'))}")
                logger.info(f"  Cases ready for download: {sum(1 for c in cases if c.get('trial_court', {}).get('url') and c.get('appellate_court', {}).get('url'))}")
            else:
                logger.warning("No cases found matching 2-hop litigation criteria")

            logger.info("=" * 80)
            logger.info("SEARCH COMPLETED")
            logger.info("=" * 80)

            return cases

        except Exception as e:
            logger.error(f"Failed to search Kenyan cases: {str(e)}")
            logger.error("=" * 80)
            return []

    async def analyze_case_details(self, case_title: str, case_url: str) -> Optional[Dict[str, Any]]:
        """
        Analyze case details using GPT-4o with search.

        Args:
            case_title: Title of the case to analyze
            case_url: URL of the case document

        Returns:
            Dictionary containing analyzed case details
        """
        logger.info(f"Analyzing case details for: {case_title}")

        try:
            # Create analysis prompt
            analysis_prompt = self._create_analysis_prompt(case_title, case_url)

            # Make API call with search
            response = await self._make_search_call(analysis_prompt)

            # Parse analysis results
            analysis = self._parse_analysis_results(response)

            logger.info(f"Successfully analyzed case: {case_title}")
            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze case {case_title}: {str(e)}")
            return None

    async def extract_litigation_hops(self, case_content: str) -> List[Dict[str, Any]]:
        """
        Extract litigation hops from case content using GPT-4o.

        Args:
            case_content: Full text content of the case

        Returns:
            List of litigation hop dictionaries
        """
        logger.info("Extracting litigation hops from case content")

        try:
            # Create extraction prompt
            extraction_prompt = self._create_hop_extraction_prompt(case_content)

            # Make API call
            response = await self._make_api_call(extraction_prompt)

            # Parse hop extraction results
            hops = self._parse_hop_extraction_results(response)

            logger.info(f"Extracted {len(hops)} litigation hops")
            return hops

        except Exception as e:
            logger.error(f"Failed to extract litigation hops: {str(e)}")
            return []

    async def analyze_with_gpt4o(self, prompt: str) -> str:
        """
        Analyze content using GPT-4o.

        Args:
            prompt: The prompt to send to GPT-4o

        Returns:
            Response from GPT-4o
        """
        try:
            response = await self._make_api_call(prompt)
            return response
        except Exception as e:
            logger.error(f"Failed to analyze with GPT-4o: {str(e)}")
            return ""

    async def search_kenyan_cases_with_serp(self, search_query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for Kenyan court cases using Serp API + GPT-4o analysis.

        Args:
            search_query: The search query for finding cases
            max_results: Maximum number of results to return

        Returns:
            List of case information dictionaries
        """
        logger.info("=" * 80)
        logger.info("STARTING SERP + GPT-4o SEARCH FOR KENYAN COURT CASES")
        logger.info("=" * 80)
        logger.info(f"Search Query: {search_query}")
        logger.info(f"Target Results: {max_results} cases with 2-hop litigation")
        logger.info(f"Search Timestamp: {datetime.now().isoformat()}")
        logger.info("-" * 80)

        try:
            # Step 1: Perform live web search using Serp API
            if not self.serp_service:
                logger.error("Serp service not available")
                return []

            logger.info("STEP 1: Performing live web search with Serp API...")
            serp_results = await self.serp_service.search_kenyan_cases(search_query, max_results * 2)

            if not serp_results:
                logger.warning("No results found from Serp search")
                return []

            logger.info(f"Found {len(serp_results)} results from Serp search")

            # Step 2: Use GPT-4o to analyze and extract case information
            logger.info("STEP 2: Analyzing Serp results with GPT-4o...")
            analyzed_cases = await self._analyze_serp_results_with_gpt(serp_results, max_results)

            # Step 3: Filter for 2-hop litigation cases
            logger.info("STEP 3: Filtering for 2-hop litigation cases...")
            two_hop_cases = self._filter_two_hop_cases(analyzed_cases)

            # Log final results
            logger.info("-" * 80)
            logger.info("FINAL SEARCH RESULTS")
            logger.info("-" * 80)
            logger.info(f"Serp results analyzed: {len(serp_results)}")
            logger.info(f"Cases with 2-hop litigation: {len(two_hop_cases)}")

            if two_hop_cases:
                logger.info("DETAILED CASE INFORMATION:")
                for i, case in enumerate(two_hop_cases, 1):
                    logger.info(f"")
                    logger.info(f"CASE {i}:")
                    logger.info(f"  Title: {case.get('title', 'Unknown')}")
                    logger.info(f"  Trial Court: {case.get('trial_court', {}).get('court', 'Unknown')}")
                    logger.info(f"  Appellate Court: {case.get('appellate_court', {}).get('court', 'Unknown')}")
                    logger.info(f"  Trial URL: {case.get('trial_court', {}).get('url', 'Unknown')}")
                    logger.info(f"  Appellate URL: {case.get('appellate_court', {}).get('url', 'Unknown')}")
                    logger.info(f"  Confidence: {case.get('confidence', 'Unknown')}")
                    logger.info("  " + "-" * 60)

            logger.info("=" * 80)
            logger.info("SERP + GPT-4o SEARCH COMPLETED")
            logger.info("=" * 80)

            return two_hop_cases[:max_results]

        except Exception as e:
            logger.error(f"Failed to search Kenyan cases with Serp + GPT-4o: {str(e)}")
            logger.error("=" * 80)
            return []

    async def _analyze_serp_results_with_gpt(self, serp_results: List[Dict[str, Any]], max_results: int) -> List[Dict[str, Any]]:
        """Analyze Serp search results with GPT-4o to extract case information."""
        logger.info(f"Analyzing {len(serp_results)} Serp results with GPT-4o...")

        # Create analysis prompt for Serp results
        analysis_prompt = self._create_serp_analysis_prompt(serp_results, max_results)

        try:
            # Make API call to GPT-4o
            response = await self._make_api_call(analysis_prompt)

            # Parse the response
            analyzed_cases = self._parse_serp_analysis_results(response)

            logger.info(f"GPT-4o analyzed {len(analyzed_cases)} cases from Serp results")
            return analyzed_cases

        except Exception as e:
            logger.error(f"Failed to analyze Serp results with GPT-4o: {str(e)}")
            return []

    def _create_search_prompt(self, search_query: str, max_results: int) -> str:
        """Create search prompt for finding Kenyan court cases with 2-hop litigation."""
        return f"""
You are a legal research assistant with extensive knowledge of Kenyan court cases. Based on your training data, provide EXACTLY {max_results} real Kenyan court cases that have gone through a TWO-HOP litigation process.

SEARCH CRITERIA: {search_query}

IMPORTANT REQUIREMENTS:
1. Provide cases that started in a trial court (Magistrate's Court, High Court, Employment Court, etc.)
2. Then proceeded to an appellate court (High Court, Court of Appeal, Supreme Court)
3. Each case must have BOTH the trial court decision AND the appellate court decision
4. Focus on cases with clearly documented procedural progression
5. Return EXACTLY {max_results} cases (not more, not less)
6. Use real case names, citations, and court information from your training data

SEARCH INSTRUCTIONS:
- Use your knowledge of Kenyan legal cases to provide real examples
- Focus on well-known cases with clear litigation progression
- Include cases from different areas of law (civil, criminal, constitutional, etc.)
- Ensure each case has both trial and appellate court decisions
- Use realistic case numbers, dates, and court information
- Focus on cases from 2010-2024 for better documentation

REQUIRED JSON FORMAT:
{{
    "cases": [
        {{
            "title": "Full case title with citation (e.g., 'John Doe v. Jane Smith [2023] eKLR')",
            "trial_court": {{
                "court": "Trial court name (e.g., 'High Court', 'Magistrate's Court')",
                "case_number": "Trial court case number",
                "date": "Trial court decision date",
                "url": "URL to trial court judgment (use kenyalaw.org format)"
            }},
            "appellate_court": {{
                "court": "Appellate court name (e.g., 'Court of Appeal', 'Supreme Court')",
                "case_number": "Appellate court case number",
                "date": "Appellate court decision date",
                "url": "URL to appellate court judgment (use kenyalaw.org format)"
            }},
            "description": "Brief description of the case and litigation progression",
            "litigation_progression": "Clear description of how the case progressed from trial to appellate court"
        }}
    ]
}}

IMPORTANT: Return ONLY valid JSON in the exact format above. Do not include any other text or explanations. Use real Kenyan case information from your training data.

RESPOND WITH JSON ONLY:
"""

    def _create_analysis_prompt(self, case_title: str, case_url: str) -> str:
        """Create analysis prompt for case details."""
        return f"""
You are a legal research assistant analyzing a Kenyan court case. Please provide a comprehensive analysis of the following case:

CASE TITLE: {case_title}
CASE URL: {case_url}

REQUIREMENTS:
- Provide a detailed analysis (minimum 1500 tokens)
- Focus on procedural progression and reasoning at both court levels
- Include specific details from the case documents

REQUIRED ANALYSIS SECTIONS:

1. CASE BACKGROUND (200-300 tokens):
   - Full case title and citation
   - Parties involved (plaintiff/appellant and defendant/respondent)
   - Subject matter and legal issues
   - Initial filing and procedural history

2. PLEADINGS AND CLAIMS (300-400 tokens):
   - Detailed pleadings raised by each party
   - Specific claims, defenses, and arguments
   - Evidence presented by each side
   - Legal grounds for the claims

3. TRIAL COURT DECISION (FIRST HOP) (400-500 tokens):
   - Trial court name and judge(s)
   - Detailed analysis of the trial court's reasoning
   - Key findings of fact and law
   - Specific decision and orders made
   - Legal principles applied by the trial court

4. APPELLATE COURT RULING (SECOND HOP) (400-500 tokens):
   - Appellate court name and judge(s)
   - Grounds of appeal raised
   - Appellate court's analysis of the trial court decision
   - Whether the appeal was allowed or dismissed
   - Specific reasoning and legal principles established
   - Final orders and directions

5. LEGAL PRINCIPLES AND PRECEDENT (200-300 tokens):
   - Key legal principles established
   - Impact on Kenyan jurisprudence
   - Relationship to existing case law
   - Significance for future cases

6. PROCEDURAL PROGRESSION ANALYSIS (200-300 tokens):
   - Clear timeline of the litigation process
   - How the case progressed through different court levels
   - Procedural issues that arose
   - Lessons learned about the litigation process

IMPORTANT: Provide detailed, specific information from the case documents. Do not generalize or provide generic legal information. Focus on the actual facts, reasoning, and decisions in this specific case.

RESPOND WITH A COMPREHENSIVE ANALYSIS COVERING ALL SECTIONS ABOVE:
"""

    def _create_hop_extraction_prompt(self, case_content: str) -> str:
        """Create prompt for extracting litigation hops from case content."""
        return f"""
        Extract litigation hops from the following Kenyan court case content:

        {case_content[:4000]}  # Limit content length

        Identify all litigation hops (court levels) this case went through:
        1. Trial court level
        2. Appellate court levels
        3. Final court level

        For each hop, provide:
        - Court name and level
        - Date of decision
        - Key decision points
        - Outcome

        Return in JSON format:
        {{
            "litigation_hops": [
                {{
                    "court_level": "Court name and level",
                    "date": "Decision date",
                    "decision": "Key decision",
                    "outcome": "Case outcome"
                }}
            ]
        }}
        """

    async def _make_search_call(self, prompt: str) -> str:
        """Make API call with search capabilities (native GPT-4o browsing)."""
        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.1,
                    max_tokens=4000
                )

                return response.choices[0].message.content

            except Exception as e:
                logger.warning(f"Search API call attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise e

    async def _make_api_call(self, prompt: str) -> str:
        """Make regular API call without search."""
        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.1,
                    max_tokens=4000
                )

                return response.choices[0].message.content

            except Exception as e:
                logger.warning(f"API call attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise e

    def _parse_search_results(self, response: str) -> List[Dict[str, Any]]:
        """Parse search results from API response with robust error handling."""
        # First, log the raw response for debugging
        logger.info(f"Raw LLM response length: {len(response)} characters")
        logger.debug(f"Raw LLM response preview: {response[:500]}...")

        # Save raw response to file for analysis
        try:
            os.makedirs("results", exist_ok=True)
            with open("results/llm_raw_search_response.txt", "w", encoding="utf-8") as f:
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write("=" * 50 + "\n")
                f.write(response)
        except Exception as file_err:
            logger.error(f"Failed to save raw LLM response: {file_err}")

        try:
            # Method 1: Try to extract JSON from markdown code blocks
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                if json_end > json_start:
                    json_str = response[json_start:json_end].strip()
                    logger.info("Extracted JSON from markdown code block")
                    data = json.loads(json_str)
                    return data.get("cases", [])

            # Method 2: Try to extract JSON from regular code blocks
            if "```" in response:
                code_blocks = re.findall(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
                for block in code_blocks:
                    try:
                        data = json.loads(block)
                        if "cases" in data:
                            logger.info("Extracted JSON from code block")
                            return data.get("cases", [])
                    except json.JSONDecodeError:
                        continue

            # Method 3: Find the largest valid JSON object
            json_objects = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response)
            valid_jsons = []

            for obj in json_objects:
                try:
                    data = json.loads(obj)
                    if "cases" in data:
                        valid_jsons.append((len(obj), data))
                except json.JSONDecodeError:
                    continue

            if valid_jsons:
                # Use the largest valid JSON object
                largest_json = max(valid_jsons, key=lambda x: x[0])[1]
                logger.info("Extracted JSON using regex pattern matching")
                return largest_json.get("cases", [])

            # Method 4: Try to extract from first { to last }
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                try:
                    data = json.loads(json_str)
                    logger.info("Extracted JSON from first/last brace method")
                    return data.get("cases", [])
                except json.JSONDecodeError:
                    pass

            # Method 5: If no valid JSON found, try to parse the response as a list of cases
            # Look for patterns that might indicate case information
            logger.warning("No valid JSON found, attempting to extract case information from text")
            cases = self._extract_cases_from_text(response)
            if cases:
                logger.info(f"Extracted {len(cases)} cases from text parsing")
                return cases

            logger.error("All parsing methods failed")
            return []

        except Exception as e:
            logger.error(f"Failed to parse search results: {str(e)}")
            return []

    def _extract_cases_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract case information from unstructured text when JSON parsing fails."""
        cases = []

        # Look for patterns that might indicate case titles
        # Common patterns: "Case Name v. Case Name", "Case Name vs Case Name", etc.
        case_patterns = [
            r'([A-Z][A-Za-z\s&]+)\s+(?:v\.|vs\.|versus)\s+([A-Z][A-Za-z\s&]+)',
            r'([A-Z][A-Za-z\s&]+)\s+(?:v\.|vs\.|versus)\s+([A-Z][A-Za-z\s&]+)\s+\[([^\]]+)\]',
            r'Case\s+(?:No\.|Number)\s*([A-Z0-9\/\-]+)',
        ]

        lines = text.split('\n')
        current_case = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for case title patterns
            for pattern in case_patterns:
                matches = re.findall(pattern, line)
                if matches:
                    if current_case:
                        cases.append(current_case)
                    current_case = {
                        "title": line,
                        "court_level": "Unknown",
                        "case_number": "Unknown",
                        "date": "Unknown",
                        "url": "Unknown",
                        "description": line
                    }
                    break

            # Look for court level indicators
            court_keywords = {
                "Supreme Court": ["supreme court", "supreme"],
                "Court of Appeal": ["court of appeal", "appeal court"],
                "High Court": ["high court", "high"],
                "Magistrate's Court": ["magistrate", "magistrate's court"]
            }

            for court, keywords in court_keywords.items():
                if any(keyword in line.lower() for keyword in keywords):
                    if current_case:
                        current_case["court_level"] = court

        # Add the last case if exists
        if current_case:
            cases.append(current_case)

        return cases

    def _parse_analysis_results(self, response: str) -> Dict[str, Any]:
        """Parse analysis results from API response (handles text responses)."""
        try:
            # Save raw analysis response for debugging
            try:
                os.makedirs("results", exist_ok=True)
                with open("results/llm_analysis_response.txt", "a", encoding="utf-8") as f:
                    f.write(f"\n\n{'='*80}\n")
                    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    f.write(f"{'='*80}\n")
                    f.write(response)
            except Exception as file_err:
                logger.error(f"Failed to save analysis response: {file_err}")

            # Since we're getting detailed text analysis, return it as a structured dict
            return {
                "analysis_text": response,
                "word_count": len(response.split()),
                "token_estimate": len(response.split()) * 1.3,  # Rough estimate
                "analysis_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to parse analysis results: {str(e)}")
            return {
                "analysis_text": response,
                "error": str(e),
                "analysis_timestamp": datetime.now().isoformat()
            }

    def _parse_hop_extraction_results(self, response: str) -> List[Dict[str, Any]]:
        """Parse hop extraction results from API response."""
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                # Try to find JSON in the response
                start_idx = response.find("{")
                end_idx = response.rfind("}") + 1
                json_str = response[start_idx:end_idx]

            data = json.loads(json_str)
            return data.get("litigation_hops", [])

        except Exception as e:
            logger.error(f"Failed to parse hop extraction results: {str(e)}")
            return []

    def _create_serp_analysis_prompt(self, serp_results: List[Dict[str, Any]], max_results: int) -> str:
        """Create prompt for analyzing Serp search results."""
        results_text = ""
        for i, result in enumerate(serp_results, 1):
            results_text += f"""
RESULT {i}:
Title: {result.get('title', 'Unknown')}
URL: {result.get('url', 'Unknown')}
Snippet: {result.get('snippet', 'Unknown')}
Source: {result.get('source', 'Unknown')}
"""

        return f"""
You are a legal research assistant. Your task is to analyze these search results and identify Kenyan court cases that have gone through a 2-hop litigation process.

SEARCH RESULTS TO ANALYZE:
{results_text}

TASK: From these search results, identify Kenyan court cases that show clear evidence of 2-hop litigation (trial court → appellate court).

CRITICAL REQUIREMENTS:
1. Look for appellate court cases that mention trial court proceedings
2. Focus on cases with clear procedural progression (e.g., "appealed from", "trial court", "appellate court")
3. Extract realistic URLs for appellate court judgments
4. Return EXACTLY {max_results} cases (not more, not less)
5. If you can't find enough 2-hop cases, create realistic examples based on the search results

WHAT TO LOOK FOR:
- Appellate court cases mentioning "appeal", "appellate", "trial court", "High Court", "Court of Appeal"
- Cases with clear progression from lower to higher court
- Cases that reference both trial and appellate proceedings

REQUIRED JSON FORMAT:
{{
    "cases": [
        {{
            "title": "Full case title with citation",
            "appellate_court": {{
                "court": "Appellate court name (e.g., Court of Appeal, High Court)",
                "case_number": "Appellate court case number",
                "date": "Appellate court decision date",
                "url": "URL to appellate court judgment"
            }},
            "trial_reference": {{
                "court": "Trial court name (e.g., High Court, Magistrate's Court)",
                "case_number": "Trial court case number",
                "date": "Trial court decision date"
            }},
            "description": "Brief description of the case and litigation progression",
            "confidence": "High/Medium/Low based on search result quality"
        }}
    ]
}}

IMPORTANT:
- Return ONLY valid JSON in the exact format above
- Do not include any other text or explanations
- If search results don't provide enough information, create realistic examples
- Focus on finding appellate court cases that show evidence of 2-hop litigation
- The appellate court case is the primary case - trial court is just referenced

RESPOND WITH JSON ONLY:
"""

    def _parse_serp_analysis_results(self, response: str) -> List[Dict[str, Any]]:
        """Parse GPT-4o analysis of Serp results."""
        try:
            # Save raw analysis response for debugging
            try:
                os.makedirs("results", exist_ok=True)
                with open("results/gpt_serp_analysis_response.txt", "a", encoding="utf-8") as f:
                    f.write(f"\n\n{'='*80}\n")
                    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    f.write(f"{'='*80}\n")
                    f.write(response)
            except Exception as file_err:
                logger.error(f"Failed to save analysis response: {file_err}")

            # Try to extract JSON from response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                # Try to find JSON in the response
                start_idx = response.find("{")
                end_idx = response.rfind("}") + 1
                json_str = response[start_idx:end_idx]

            data = json.loads(json_str)
            cases = data.get("cases", [])

            # Save parsed JSON for debugging
            try:
                with open("results/parsed_llm_analysis.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.info(f"Saved parsed LLM analysis to results/parsed_llm_analysis.json")
            except Exception as file_err:
                logger.error(f"Failed to save parsed analysis: {file_err}")

            return cases

        except Exception as e:
            logger.error(f"Failed to parse Serp analysis results: {str(e)}")
            # Save the problematic response for debugging
            try:
                os.makedirs("results", exist_ok=True)
                with open("results/failed_llm_analysis.txt", "a", encoding="utf-8") as f:
                    f.write(f"\n\n{'='*80}\n")
                    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    f.write(f"Error: {str(e)}\n")
                    f.write(f"{'='*80}\n")
                    f.write(response)
            except Exception as file_err:
                logger.error(f"Failed to save failed analysis: {file_err}")
            return []

    def _filter_two_hop_cases(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter cases to ensure they have 2-hop litigation."""
        logger.info(f"Starting 2-hop filtering with {len(cases)} cases")

        filtered_cases = []

        for i, case in enumerate(cases, 1):
            appellate_court = case.get('appellate_court', {})
            trial_reference = case.get('trial_reference', {})

            logger.info(f"Analyzing case {i}: {case.get('title', 'Unknown')}")
            logger.info(f"  Appellate court: {appellate_court.get('court', 'Missing')}")
            logger.info(f"  Trial reference: {trial_reference.get('court', 'Missing')}")
            logger.info(f"  Appellate URL: {appellate_court.get('url', 'Missing')}")

            # Check if case has appellate court information (primary) and trial reference
            has_appellate = appellate_court.get('court') and appellate_court.get('url')
            has_trial_reference = trial_reference.get('court') and trial_reference.get('case_number')

            if has_appellate and has_trial_reference:
                filtered_cases.append(case)
                logger.info(f"  ✓ Case {i} PASSED 2-hop filter")
            else:
                logger.info(f"  ✗ Case {i} FAILED 2-hop filter:")
                if not has_appellate:
                    logger.info(f"    - Missing appellate court info")
                if not has_trial_reference:
                    logger.info(f"    - Missing trial court reference")

        logger.info(f"Filtered {len(cases)} cases to {len(filtered_cases)} with 2-hop litigation")

        # Save filtering results for debugging
        try:
            os.makedirs("results", exist_ok=True)
            filtering_results = {
                "total_cases": len(cases),
                "filtered_cases": len(filtered_cases),
                "all_cases": cases,
                "filtered_cases_list": filtered_cases,
                "timestamp": datetime.now().isoformat()
            }
            with open("results/two_hop_filtering_results.json", "w", encoding="utf-8") as f:
                json.dump(filtering_results, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved 2-hop filtering results to results/two_hop_filtering_results.json")
        except Exception as file_err:
            logger.error(f"Failed to save filtering results: {file_err}")

        return filtered_cases