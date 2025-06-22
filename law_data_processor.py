#!/usr/bin/env python3
"""
Legal Assistant Backend - Main Entry Point

This script provides the main entry point for the Legal Assistant backend system.
It orchestrates the complete workflow from prompt processing to final analysis.
"""

import asyncio
import argparse
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from loguru import logger

# Import services
from backend.services.prompt_processor import PromptProcessor
from backend.services.llm_service import LLMService
from backend.services.pdf_downloader import PDFDownloader
from backend.services.case_analyzer import CaseAnalyzer
from backend.services.pdf_analysis_service import PDFAnalysisService
from backend.services.cache_service import CacheService
from backend.utils.config import get_config

# Configure logging
logger.add("logs/legal_assistant.log", rotation="1 day", retention="7 days", level="INFO")

def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Legal Assistant Backend - Process legal research queries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python law_data_processor.py --query "contract dispute" --max_results 5
  python law_data_processor.py --query "land ownership" --max_results 3 --download_pdfs
  python law_data_processor.py --query "criminal appeal" --max_results 10 --no_analysis
        """
    )

    parser.add_argument(
        "--query", "-q",
        type=str,
        default="Find Kenyan court cases with 2-hop litigation processes",
        help="Search query for legal cases (default: Find Kenyan court cases with 2-hop litigation processes)"
    )

    parser.add_argument(
        "--max_results", "-m",
        type=int,
        default=5,
        help="Maximum number of results to return (default: 5)"
    )

    parser.add_argument(
        "--download_pdfs", "-d",
        action="store_true",
        help="Download PDFs for found cases"
    )

    parser.add_argument(
        "--no_analysis", "-n",
        action="store_true",
        help="Skip case analysis step"
    )

    parser.add_argument(
        "--output_file", "-o",
        type=str,
        default="results/final_analysis_results.json",
        help="Output file path for results (default: results/final_analysis_results.json)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser

async def run_complete_workflow(
    query: str,
    max_results: int = 5,
    download_pdfs: bool = True,
    perform_analysis: bool = True,
    output_file: str = "results/final_analysis_results.json",
    config=None
) -> Dict[str, Any]:
    """
    Run the complete legal assistant workflow

    Args:
        query: Search query
        max_results: Maximum number of results
        download_pdfs: Whether to download PDFs
        perform_analysis: Whether to perform case analysis
        output_file: Output file path
        config: Configuration object

    Returns:
        Dictionary containing workflow results
    """
        logger.info("Starting complete legal assistant workflow")

        # Step 1: Process initial prompt
        logger.info("Step 1: Processing initial prompt")
    prompt_processor = PromptProcessor()
    prompt_result = prompt_processor.process_prompt(query)
            logger.info(f"✓ Prompt processing completed: {prompt_result}")

        # Step 2: Perform Serp search and LLM analysis
        logger.info("Step 2: Performing Serp search and LLM analysis")
    llm_service = LLMService(api_key=config.openai_api_key)
    search_results = await llm_service.search_kenyan_cases_with_serp(
        search_query=query,
        max_results=max_results
    )
    logger.info(f"✓ Serp+LLM search completed. Found {len(search_results)} cases with 2-hop litigation")

        # Step 3: Filter cases ending in appellate courts
        logger.info("Step 3: Filtering cases ending in appellate courts")
    appellate_cases = []
    for i, case in enumerate(search_results, 1):
        logger.info(f"Analyzing case {i}: {case.get('title', 'Unknown')}")
        appellate_court = case.get('appellate_court', '')
                if isinstance(appellate_court, dict):
            appellate_court = appellate_court.get('court', '')
        appellate_court_lower = appellate_court.lower()

        # Check if case ends in appellate court
        if any(keyword in appellate_court_lower for keyword in ['court of appeal', 'supreme court']):
            logger.info(f"  ✓ Case {i} PASSED filter")
            appellate_cases.append(case)
        else:
            logger.info(f"  ✗ Case {i} FAILED filter (appellate court: {appellate_court})")

    logger.info(f"✓ Filtering completed. {len(appellate_cases)} cases end in appellate courts")

        # Step 4: Download PDFs
    if download_pdfs and appellate_cases:
        logger.info("Step 4: Downloading PDFs")
        pdf_downloader = PDFDownloader()

        # Extract URLs for download
        case_urls = []
        for case in appellate_cases:
            appellate_url = case.get('appellate_court', {}).get('url', '')
            if appellate_url:
                case_urls.append(appellate_url)

        if case_urls:
            download_results = await pdf_downloader.download_multiple_cases(case_urls)
            successful_downloads = sum(1 for result in download_results if result.get('success', False))
            logger.info(f"✓ PDF downloads completed. {successful_downloads}/{len(case_urls)} successful")
        else:
            logger.warning("No URLs found for PDF download")
            download_results = []
    else:
        logger.info("Skipping PDF download")
        download_results = []

        # Step 5: Analyze cases
    if perform_analysis and appellate_cases:
        logger.info("Step 5: Analyzing cases")
        case_analyzer = CaseAnalyzer()

        analysis_results = []
        for case in appellate_cases:
            case_title = case.get('title', 'Unknown')
            logger.info(f"Analyzing case: {case_title}")
            analysis_result = await case_analyzer.analyze_case(case)
            analysis_results.append(analysis_result)
            logger.info(f"Case analysis completed for: {case_title}")

        logger.info(f"✓ Case analysis completed. {len(analysis_results)}/{len(appellate_cases)} successful")
    else:
        logger.info("Skipping case analysis")
        analysis_results = []

        # Step 6: Process PDFs and perform detailed analysis
    if perform_analysis and download_results:
        logger.info("Step 6: Processing PDFs and performing detailed analysis")
        pdf_analysis_service = PDFAnalysisService()

        # Find PDF files for analysis
        pdf_files = []
        for download_result in download_results:
            if download_result.get('success', False):
                pdf_files.extend(download_result.get('pdf_files', []))

            logger.info(f"Found {len(pdf_files)} PDF files for detailed analysis")

        analysis_count = 0
            for pdf_file in pdf_files:
            try:
                filename = pdf_file.get('filename', '')
                logger.info(f"Starting PDF analysis for: {filename}")
                analysis_result = await pdf_analysis_service.analyze_pdf_file(filename)
                if analysis_result:
                    analysis_count += 1
            except Exception as e:
                logger.error(f"Error analyzing PDF {filename}: {str(e)}")

        logger.info(f"✓ PDF analysis completed. {analysis_count}/{len(pdf_files)} successful")
    else:
        logger.info("Skipping PDF analysis")

    # Step 7: Format final results
        logger.info("Step 7: Formatting final results")

        final_results = {
        "workflow_summary": {
            "query": query,
            "max_results_requested": max_results,
            "total_cases_found": len(search_results),
            "appellate_cases": len(appellate_cases),
            "pdfs_downloaded": len([r for r in download_results if r.get('success', False)]),
            "cases_analyzed": len(analysis_results),
            "timestamp": datetime.now().isoformat()
        },
        "search_results": search_results,
        "appellate_cases": appellate_cases,
        "download_results": download_results,
        "analysis_results": analysis_results
        }

        # Save results
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"✓ Results saved to {output_file}")

    return final_results

async def main():
    """Main entry point"""
    logger.info("Legal Assistant Backend starting...")

    # Parse command line arguments
    parser = setup_argument_parser()
    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logger.remove()
        logger.add("logs/legal_assistant.log", rotation="1 day", retention="7 days", level="DEBUG")
        logger.add(lambda msg: print(msg), level="DEBUG")

    # Load configuration
    try:
        config = get_config()
    logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return

    # Initialize services
    logger.info("Initializing services...")
    try:
        # Initialize cache service
        cache_service = CacheService()
        logger.info("Cache service initialized")

        # Initialize other services
        prompt_processor = PromptProcessor()
        llm_service = LLMService(api_key=config.openai_api_key)
        pdf_downloader = PDFDownloader()
        case_analyzer = CaseAnalyzer()
        pdf_analysis_service = PDFAnalysisService()

    logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        return

    # Start complete workflow
    logger.info("Starting complete legal assistant workflow")
    try:
        results = await run_complete_workflow(
            query=args.query,
            max_results=args.max_results,
            download_pdfs=args.download_pdfs,
            perform_analysis=not args.no_analysis,
            output_file=args.output_file,
            config=config
        )

            logger.info("=== WORKFLOW COMPLETED SUCCESSFULLY ===")
        logger.info(f"Steps completed: {list(results.keys())}")
        logger.info(f"Final results saved to: {args.output_file}")

    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())