#!/usr/bin/env python3
"""
Legal Assistant Backend - Main Data Processor

This script orchestrates the complete workflow for finding and analyzing
Kenyan court cases with multi-hop litigation processes.
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv
from loguru import logger
import asyncio
from datetime import datetime

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

# Import from the new modular structure
from src import (
    PromptProcessor,
    SerpSearchService,
    LLMService,
    PDFDownloader,
    CaseAnalyzer,
    ResultFormatter,
    CacheService,
    PDFAnalysisService,
    PDFExtractor,
    PDFAnalyzer
)


def setup_logging() -> None:
    """Setup logging configuration."""
    logger.remove()  # Remove default handler
    logger.add(
        "logs/legal_assistant.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    logger.add(
        sys.stderr,
        level="INFO",
        format="{time:HH:mm:ss} | {level} | {message}"
    )


def load_config() -> Dict[str, str]:
    """Load configuration from environment variables."""
    config = {
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'serp_api_key': os.getenv('SERP_API_KEY'),
        'cache_file': os.getenv('CACHE_FILE', 'cache/legal_cases_cache.json'),
        'results_dir': os.getenv('RESULTS_DIR', 'results'),
        'data_dir': os.getenv('DATA_DIR', 'data'),
        'logs_dir': os.getenv('LOGS_DIR', 'logs')
    }

    # Validate required API keys
    if not config['openai_api_key']:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    if not config['serp_api_key']:
        raise ValueError("SERP_API_KEY environment variable is required")

    # Create directories
    for dir_path in [config['results_dir'], config['data_dir'], config['logs_dir']]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    return config


def initialize_services(config: Dict[str, str]) -> Dict[str, Any]:
    """Initialize all services with configuration."""
    logger.info("Initializing services...")

    cache_service = CacheService(config['cache_file'])
    services = {
        'prompt_processor': PromptProcessor(),
        'serp_search': SerpSearchService(config['serp_api_key']),
        'llm_service': LLMService(config['openai_api_key'], serp_service=SerpSearchService(config['serp_api_key'])),
        'pdf_downloader': PDFDownloader(cache_service=cache_service),
        'case_analyzer': CaseAnalyzer(),
        'result_formatter': ResultFormatter(),
        'cache_service': cache_service,
        'pdf_analysis': PDFAnalysisService(openai_api_key=config['openai_api_key'], cache_service=cache_service),
        'pdf_extractor': PDFExtractor(),
        'pdf_analyzer': PDFAnalyzer()
    }

    logger.info("All services initialized successfully")
    return services


async def run_complete_workflow(services: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the complete legal assistant workflow.

    Args:
        services: Dictionary of initialized services
        config: Configuration dictionary

    Returns:
        Workflow results dictionary
    """
    workflow_results = {
        'success': False,
        'steps_completed': [],
        'errors': [],
        'start_time': datetime.now().isoformat()
    }

    try:
        logger.info("Starting complete legal assistant workflow")

        # Step 1: Process initial prompt
        logger.info("Step 1: Processing initial prompt")
        prompt_text = "Find Kenyan court cases with 2-hop litigation processes"
        try:
            prompt_result = services['prompt_processor'].process_prompt(prompt_text)
            logger.info(f"✓ Prompt processing completed: {prompt_result}")
            workflow_results['steps_completed'].append('prompt_processing')
        except Exception as e:
            workflow_results['errors'].append(f"Prompt processing failed: {e}")
            logger.error(f"Prompt processing failed: {e}")
            return workflow_results

        # Step 2: Perform Serp search and LLM analysis
        logger.info("Step 2: Performing Serp search and LLM analysis")
        try:
            llm_cases = await services['llm_service'].search_kenyan_cases_with_serp(
                prompt_result.text,
                max_results=5
            )

            if not llm_cases:
                workflow_results['errors'].append("No cases found by LLMService.")
                return workflow_results

            logger.info(f"✓ Serp+LLM search completed. Found {len(llm_cases)} cases with 2-hop litigation")
            workflow_results['steps_completed'].append('serp_llm_search')
        except Exception as e:
            workflow_results['errors'].append(f"Serp+LLM search failed: {e}")
            logger.error(f"Serp+LLM search failed: {e}")
            return workflow_results

        # Step 3: Filter cases ending in appellate courts
        logger.info("Step 3: Filtering cases ending in appellate courts")
        filtered_cases = []
        for i, case in enumerate(llm_cases):
            logger.info(f"Analyzing case {i+1}: {case.get('title', 'Unknown')}")
            if isinstance(case, dict):
                appellate_court = case.get('appellate_court', {})
                trial_reference = case.get('trial_reference', {})

                if isinstance(appellate_court, dict):
                    court_name = appellate_court.get('court', '').lower()
                    logger.info(f"  Appellate court (dict): {court_name}")
                    if 'court of appeal' in court_name or 'supreme court' in court_name:
                        filtered_cases.append(case)
                        logger.info(f"  ✓ Case {i+1} PASSED filter")
                elif isinstance(appellate_court, str):
                    court_name = appellate_court.lower()
                    logger.info(f"  Appellate court (string): {court_name}")
                    if 'court of appeal' in court_name or 'supreme court' in court_name:
                        filtered_cases.append(case)
                        logger.info(f"  ✓ Case {i+1} PASSED filter")

        logger.info(f"✓ Filtering completed. {len(filtered_cases)} cases end in appellate courts")
        workflow_results['steps_completed'].append('filtering')

        # Step 4: Download PDFs
        logger.info("Step 4: Downloading PDFs")
        try:
            download_results = await services['pdf_downloader'].download_multiple_cases(filtered_cases)
            successful_downloads = len([r for r in download_results if r.get('success', False)])
            logger.info(f"✓ PDF downloads completed. {successful_downloads}/{len(download_results)} successful")
            workflow_results['steps_completed'].append('pdf_download')
        except Exception as e:
            workflow_results['errors'].append(f"PDF download failed: {e}")
            logger.error(f"PDF download failed: {e}")
            return workflow_results

        # Step 5: Analyze cases
        logger.info("Step 5: Analyzing cases")
        try:
            analysis_tasks = []
            for case in filtered_cases:
                if isinstance(case, dict):
                    analysis_tasks.append(services['case_analyzer'].analyze_case(case))

            analysis_results = await asyncio.gather(*analysis_tasks)
            successful_analyses = len([r for r in analysis_results if r.get('success', False)])
            logger.info(f"✓ Case analysis completed. {successful_analyses}/{len(analysis_results)} successful")
            workflow_results['steps_completed'].append('case_analysis')
        except Exception as e:
            workflow_results['errors'].append(f"Case analysis failed: {e}")
            logger.error(f"Case analysis failed: {e}")
            return workflow_results

        # Step 6: Process PDFs and perform detailed analysis
        logger.info("Step 6: Processing PDFs and performing detailed analysis")
        pdf_analysis_results = []

        # Get list of downloaded PDFs
        pdf_dir = Path(config['data_dir']) / "raw"
        if pdf_dir.exists():
            pdf_files = list(pdf_dir.glob("*.pdf"))
            logger.info(f"Found {len(pdf_files)} PDF files for detailed analysis")

            for pdf_file in pdf_files:
                case_title = pdf_file.stem
                analysis_result = await services['pdf_analysis'].analyze_pdf_file(
                    str(pdf_file),
                    case_title
                )
                pdf_analysis_results.append(analysis_result)

        successful_pdf_analyses = len([r for r in pdf_analysis_results if r.get('success', False)])
        logger.info(f"✓ PDF analysis completed. {successful_pdf_analyses}/{len(pdf_analysis_results)} successful")
        workflow_results['steps_completed'].append('pdf_analysis')

        # Step 7: Format results
        logger.info("Step 7: Formatting final results")
        final_results = {
            'workflow_summary': {
                'total_cases_found': len(llm_cases),
                'cases_with_2hop_litigation': len(llm_cases),
                'cases_ending_in_appellate': len(filtered_cases),
                'pdfs_downloaded': successful_downloads,
                'cases_analyzed': successful_analyses,
                'pdfs_analyzed': successful_pdf_analyses,
                'steps_completed': workflow_results['steps_completed']
            },
            'llm_search_results': llm_cases,
            'filtered_cases': filtered_cases,
            'download_results': download_results,
            'case_analysis': analysis_results,
            'pdf_analysis': pdf_analysis_results
        }

        # Save results
        results_file = Path(config['results_dir']) / "final_analysis_results.json"
        results_file.parent.mkdir(exist_ok=True)

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"✓ Results saved to {results_file}")
        workflow_results['success'] = True
        workflow_results['final_results'] = final_results

    except Exception as e:
        workflow_results['errors'].append(f"Workflow error: {e}")
        logger.error(f"Workflow error: {e}")

    workflow_results['end_time'] = datetime.now().isoformat()
    return workflow_results


def main():
    """Main entry point for the legal assistant backend."""
    logger.info("Legal Assistant Backend starting...")

    # Load configuration
    config = load_config()
    logger.info("Configuration loaded successfully")

    # Initialize services
    logger.info("Initializing services...")
    cache_service = CacheService(config['cache_file'])
    services = {
        'prompt_processor': PromptProcessor(),
        'serp_search': SerpSearchService(config['serp_api_key']),
        'llm_service': LLMService(config['openai_api_key'], serp_service=SerpSearchService(config['serp_api_key'])),
        'pdf_downloader': PDFDownloader(cache_service=cache_service),
        'case_analyzer': CaseAnalyzer(),
        'result_formatter': ResultFormatter(),
        'cache_service': cache_service,
        'pdf_analysis': PDFAnalysisService(openai_api_key=config['openai_api_key'], cache_service=cache_service),
        'pdf_extractor': PDFExtractor(),
        'pdf_analyzer': PDFAnalyzer()
    }
    logger.info("All services initialized successfully")

    # Run the complete workflow
    logger.info("Starting complete legal assistant workflow")
    try:
        results = asyncio.run(run_complete_workflow(services, config))

        if results['success']:
            logger.info("=== WORKFLOW COMPLETED SUCCESSFULLY ===")
            logger.info(f"Steps completed: {results['steps_completed']}")
            logger.info(f"Final results saved to: {config['results_dir']}/final_analysis_results.json")
        else:
            logger.error("=== WORKFLOW FAILED ===")
            logger.error(f"Errors: {results['errors']}")

    except Exception as e:
        logger.error("=== WORKFLOW FAILED ===")
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()