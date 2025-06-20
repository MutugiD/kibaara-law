#!/usr/bin/env python3
"""
Legal Assistant Backend - Main Script

This script orchestrates the workflow for finding and analyzing Kenyan court cases
with multi-hop litigation processes using live web search and GPT-4o.
"""

import asyncio
import os
from typing import List, Dict, Any
from loguru import logger
from datetime import datetime
from dotenv import load_dotenv

# Import services
from src.services.prompt_processor import PromptProcessor
from src.services.llm_service import LLMService
from src.services.serp_search_service import SerpSearchService
from src.services.kenya_law_scraper import KenyaLawScraper
from src.services.document_downloader import DocumentDownloader
from src.services.case_analyzer import CaseAnalyzer
from src.services.result_formatter import ResultFormatter

# Import models
from src.models.case_models import Case, CaseMetadata, LitigationHop, CourtLevel, CaseStatus


class LegalAssistantBackend:
    """
    Main backend orchestrator for legal assistant functionality.

    This class coordinates all services to find, download, and analyze
    Kenyan court cases with 2-hop litigation processes.
    """

    def __init__(self) -> None:
        """Initialize the legal assistant backend."""
        self.setup_logging()
        self.load_environment()
        self.initialize_services()

    def setup_logging(self) -> None:
        """Setup logging configuration."""
        logger.remove()
        logger.add(
            "logs/legal_assistant.log",
            rotation="10 MB",
            retention="7 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        )
        logger.add(
            lambda msg: print(msg, end=""),
            level="INFO",
            format="{time:HH:mm:ss} | {level} | {message}"
        )

    def load_environment(self) -> None:
        """Load environment variables and configuration."""
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.serp_api_key = os.getenv("SERP_API_KEY")

        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        if not self.serp_api_key:
            raise ValueError("SERP_API_KEY environment variable is required")

        logger.info("Environment variables loaded successfully")

    def initialize_services(self) -> None:
        """Initialize all service components."""
        logger.info("Initializing services...")

        # Initialize Serp search service
        self.serp_service = SerpSearchService(self.serp_api_key)
        logger.info("Serp search service initialized")

        # Initialize LLM service with Serp integration
        self.llm_service = LLMService(self.openai_api_key, self.serp_service)
        logger.info("LLM service initialized with Serp integration")

        # Initialize other services
        self.prompt_processor = PromptProcessor()
        self.kenya_law_scraper = KenyaLawScraper()
        self.document_downloader = DocumentDownloader()
        self.case_analyzer = CaseAnalyzer(self.openai_api_key)
        self.result_formatter = ResultFormatter()

        logger.info("All services initialized successfully")

    async def process_legal_request(self, user_prompt: str) -> str:
        """
        Process a legal research request end-to-end.

        Args:
            user_prompt: The user's legal research request

        Returns:
            Formatted analysis results
        """
        logger.info("=" * 100)
        logger.info("STARTING LEGAL ASSISTANT BACKEND PROCESSING")
        logger.info("=" * 100)
        logger.info(f"User Prompt: {user_prompt}")
        logger.info(f"Processing Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 100)

        try:
            # Step 1: Process and validate the user prompt
            logger.info("STEP 1: Processing user prompt...")
            prompt = self.prompt_processor.process_prompt(user_prompt)
            search_query = self._extract_search_query_from_prompt(prompt)
            logger.info(f"Extracted search query: {search_query}")
            logger.info("-" * 80)

            # Step 2: Search for Kenyan court cases using Serp + GPT-4o
            logger.info("STEP 2: Searching for Kenyan court cases with live web search...")
            cases = await self.llm_service.search_kenyan_cases_with_serp(search_query, max_results=5)

            if not cases:
                logger.warning("No cases found with 2-hop litigation")
                return "No cases with 2-hop litigation found. Please try a different search query."

            logger.info(f"Found {len(cases)} cases with 2-hop litigation")
            logger.info("-" * 80)

            # Step 3: Download case documents
            logger.info("STEP 3: Downloading case documents...")
            downloaded_cases = await self.download_case_documents(cases)

            if not downloaded_cases:
                logger.warning("No case documents could be downloaded")
                return "Unable to download case documents. Please try again later."

            logger.info(f"Successfully downloaded {len(downloaded_cases)} case documents")
            logger.info("-" * 80)

            # Step 4: Analyze cases with detailed extraction
            logger.info("STEP 4: Analyzing cases with detailed extraction...")
            analysis_results = await self.analyze_cases(downloaded_cases)

            if not analysis_results:
                logger.warning("No analysis results generated")
                return "Unable to analyze case documents. Please try again later."

            logger.info(f"Generated analysis for {len(analysis_results)} cases")
            logger.info("-" * 80)

            # Step 5: Format and return results
            logger.info("STEP 5: Formatting results...")
            formatted_results = self.result_formatter.format_results(analysis_results)

            logger.info("=" * 100)
            logger.info("LEGAL ASSISTANT BACKEND PROCESSING COMPLETED")
            logger.info("=" * 100)

            return formatted_results

        except Exception as e:
            logger.error(f"Error in legal assistant processing: {str(e)}")
            logger.error("=" * 100)
            return f"Error processing legal request: {str(e)}"

    def _extract_search_query_from_prompt(self, prompt) -> str:
        """Extract search query from processed prompt."""
        # Extract relevant information from the prompt
        criteria = prompt.search_criteria

        # Build search query based on criteria
        query_parts = []

        # Add court levels
        if criteria.court_levels:
            court_names = [level.value for level in criteria.court_levels]
            query_parts.extend(court_names)

        # Add case type
        if criteria.case_type:
            query_parts.append(criteria.case_type)

        # Add subject matter
        if criteria.subject_matter:
            query_parts.append(criteria.subject_matter)

        # Add keywords
        if criteria.keywords:
            query_parts.extend(criteria.keywords)

        # Add multi-hop requirement
        if criteria.require_multi_hop:
            query_parts.extend(["2-hop", "litigation", "trial", "appellate"])

        # Default search query if no specific criteria
        if not query_parts:
            query_parts = ["Kenya", "Court of Appeal", "cases", "2-hop", "litigation", "trial", "appellate"]

        return " ".join(query_parts)

    async def download_case_documents(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Download documents for the found cases.

        Args:
            cases: List of case information dictionaries

        Returns:
            List of cases with downloaded documents
        """
        downloaded_cases = []

        for i, case in enumerate(cases, 1):
            logger.info(f"Downloading documents for case {i}/{len(cases)}")

            try:
                # Download appellate court document (primary)
                appellate_url = case.get('appellate_court', {}).get('url', '')
                appellate_doc = None
                if appellate_url:
                    appellate_doc = await self.document_downloader.download_document(appellate_url)

                # Add downloaded documents to case
                case_with_docs = case.copy()
                case_with_docs['appellate_document'] = appellate_doc

                downloaded_cases.append(case_with_docs)
                logger.info(f"Successfully downloaded appellate document for case {i}")

            except Exception as e:
                logger.error(f"Failed to download documents for case {i}: {str(e)}")
                # Continue with other cases
                continue

        return downloaded_cases

    async def analyze_cases(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze downloaded case documents.

        Args:
            cases: List of cases with downloaded documents

        Returns:
            List of analysis results
        """
        analysis_results = []

        for i, case in enumerate(cases, 1):
            logger.info(f"Analyzing case {i}/{len(cases)}")

            try:
                # Analyze the case
                analysis = await self.case_analyzer.analyze_case(case)

                if analysis:
                    analysis_results.append(analysis)
                    logger.info(f"Successfully analyzed case {i}")
                else:
                    logger.warning(f"No analysis generated for case {i}")

            except Exception as e:
                logger.error(f"Failed to analyze case {i}: {str(e)}")
                # Continue with other cases
                continue

        return analysis_results


async def main() -> None:
    """Main entry point for the legal assistant backend."""
    try:
        # Initialize the backend
        backend = LegalAssistantBackend()

        # Example user prompt
        user_prompt = """
        Find Kenyan court cases with 2-hop litigation processes involving:
        - Trial court decisions
        - Appellate court rulings
        - Clear procedural progression
        - Recent cases (last 5 years)
        Focus on cases with detailed pleadings and judgments.
        """

        # Process the request
        results = await backend.process_legal_request(user_prompt)

        # Save results to file
        os.makedirs("results", exist_ok=True)
        with open("results/legal_analysis_result.txt", "w", encoding="utf-8") as f:
            f.write(results)

        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print("Results saved to: results/legal_analysis_result.txt")
        print("Logs saved to: logs/legal_assistant.log")
        print("=" * 80)

    except Exception as e:
        logger.error(f"Main execution error: {str(e)}")
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())