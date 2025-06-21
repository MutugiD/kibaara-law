"""
PDF Analysis Service

This service orchestrates the complete PDF analysis workflow using the new modular structure.
"""

import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from loguru import logger

from ..pdf_processor.pdf_extractor import PDFExtractor
from ..pdf_processor.pdf_analyzer import PDFAnalyzer
from ..services.cache_service import CacheService
from ..services.llm_service import LLMService


class PDFAnalysisService:
    """
    Service for orchestrating complete PDF analysis workflow.

    This service coordinates PDF extraction, analysis, and caching using
    the new modular structure with separate prompt services.
    """

    def __init__(self, cache_service: Optional[CacheService] = None,
                 llm_service: Optional[LLMService] = None,
                 openai_api_key: Optional[str] = None):
        """
        Initialize the PDF analysis service.

        Args:
            cache_service: Cache service for storing results
            llm_service: LLM service for analysis
            openai_api_key: OpenAI API key for LLMService
        """
        self.cache_service = cache_service or CacheService()
        if llm_service:
            self.llm_service = llm_service
        else:
            if openai_api_key is None:
                openai_api_key = os.getenv('OPENAI_API_KEY')
            self.llm_service = LLMService(openai_api_key)
        self.pdf_extractor = PDFExtractor()
        self.pdf_analyzer = PDFAnalyzer(self.llm_service, openai_api_key=openai_api_key)

        logger.info("PDF Analysis Service initialized with new modular structure")

    async def analyze_pdf_file(self, pdf_path: str, case_title: str,
                        force_reanalysis: bool = False) -> Dict[str, Any]:
        """
        Analyze a single PDF file.

        Args:
            pdf_path: Path to the PDF file
            case_title: Title of the case
            force_reanalysis: Whether to force reanalysis even if cached

        Returns:
            Analysis results
        """
        logger.info(f"Starting PDF analysis for: {case_title}")

        try:
            # Check cache first
            cache_key = self._generate_cache_key(case_title, pdf_path)
            if not force_reanalysis:
                cached_result = self.cache_service.get_case(cache_key)
                if cached_result:
                    logger.info(f"Found cached analysis for: {case_title}")
                    return cached_result

            # Step 1: Process the PDF
            logger.info(f"Processing PDF: {pdf_path}")
            pdf_result = self.pdf_extractor.process_pdf_file(pdf_path)

            if not pdf_result['success']:
                return {
                    'success': False,
                    'case_title': case_title,
                    'error': f"PDF processing failed: {pdf_result.get('error', 'Unknown error')}",
                    'timestamp': self._get_timestamp()
                }

            # Step 2: Analyze the processed content
            logger.info(f"Analyzing processed content for: {case_title}")
            analysis_result = await self.pdf_analyzer.analyze_case_complete(
                case_title,
                pdf_result['cleaned_text']
            )

            if not analysis_result['success']:
                return {
                    'success': False,
                    'case_title': case_title,
                    'error': f"Analysis failed: {analysis_result.get('error', 'Unknown error')}",
                    'timestamp': self._get_timestamp()
                }

            # Step 3: Combine results
            complete_result = {
                'success': True,
                'case_title': case_title,
                'pdf_processing': pdf_result,
                'analysis': analysis_result,
                'cache_key': cache_key,
                'timestamp': self._get_timestamp()
            }

            # Step 4: Cache the results
            logger.info(f"Caching analysis results for: {case_title}")
            self.cache_service.cache_case(cache_key, complete_result)

            # Step 5: Save detailed results
            self._save_detailed_results(complete_result)

            logger.info(f"Successfully completed PDF analysis for: {case_title}")
            return complete_result

        except Exception as e:
            logger.error(f"Error in PDF analysis for {case_title}: {e}")
            return {
                'success': False,
                'case_title': case_title,
                'error': str(e),
                'timestamp': self._get_timestamp()
            }

    async def analyze_multiple_pdfs(self, pdf_files: List[Dict[str, str]],
                            force_reanalysis: bool = False) -> List[Dict[str, Any]]:
        """
        Analyze multiple PDF files.

        Args:
            pdf_files: List of dictionaries with 'path' and 'title' keys
            force_reanalysis: Whether to force reanalysis even if cached

        Returns:
            List of analysis results
        """
        logger.info(f"Starting analysis of {len(pdf_files)} PDF files")

        results = []
        successful = 0
        failed = 0

        for pdf_file in pdf_files:
            pdf_path = pdf_file.get('path')
            case_title = pdf_file.get('title', 'Unknown Case')

            if not pdf_path or not os.path.exists(pdf_path):
                logger.error(f"PDF file not found: {pdf_path}")
                results.append({
                    'success': False,
                    'case_title': case_title,
                    'error': 'PDF file not found',
                    'timestamp': self._get_timestamp()
                })
                failed += 1
                continue

            result = await self.analyze_pdf_file(pdf_path, case_title, force_reanalysis)
            results.append(result)

            if result['success']:
                successful += 1
                logger.info(f"Successfully analyzed: {case_title}")
            else:
                failed += 1
                logger.error(f"Failed to analyze: {case_title}")

        logger.info(f"Batch analysis completed. {successful} successful, {failed} failed")
        return results

    async def batch_process_pdfs(self, pdf_directory: str,
                          force_reanalysis: bool = False) -> List[Dict[str, Any]]:
        """
        Process all PDF files in a directory.

        Args:
            pdf_directory: Directory containing PDF files
            force_reanalysis: Whether to force reanalysis even if cached

        Returns:
            List of analysis results
        """
        logger.info(f"Starting batch processing of PDFs in: {pdf_directory}")

        # First, process all PDFs to extract text
        pdf_results = self.pdf_extractor.batch_process_pdfs(pdf_directory)

        # Convert to analysis format
        pdf_files = []
        for result in pdf_results:
            if result['success']:
                case_title = Path(result['file_path']).stem
                pdf_files.append({
                    'path': result['file_path'],
                    'title': case_title,
                    'processed_content': result['cleaned_text']
                })

        logger.info(f"Successfully processed {len(pdf_files)} PDFs for analysis")

        # Analyze each processed PDF
        results = []
        for pdf_file in pdf_files:
            case_title = pdf_file['title']
            processed_content = pdf_file['processed_content']

            # Check cache first
            cache_key = self._generate_cache_key(case_title, pdf_file['path'])
            if not force_reanalysis:
                cached_result = self.cache_service.get_case(cache_key)
                if cached_result:
                    logger.info(f"Found cached analysis for: {case_title}")
                    results.append(cached_result)
                    continue

            try:
                # Analyze the processed content
                analysis_result = await self.pdf_analyzer.analyze_case_complete(
                    case_title,
                    processed_content
                )

                if analysis_result['success']:
                    complete_result = {
                        'success': True,
                        'case_title': case_title,
                        'pdf_processing': {
                            'success': True,
                            'file_path': pdf_file['path'],
                            'processed_content': processed_content
                        },
                        'analysis': analysis_result,
                        'cache_key': cache_key,
                        'timestamp': self._get_timestamp()
                    }

                    # Cache the results
                    self.cache_service.cache_case(cache_key, complete_result)

                    # Save detailed results
                    self._save_detailed_results(complete_result)

                    results.append(complete_result)
                    logger.info(f"Successfully analyzed: {case_title}")
                else:
                    results.append({
                        'success': False,
                        'case_title': case_title,
                        'error': f"Analysis failed: {analysis_result.get('error', 'Unknown error')}",
                        'timestamp': self._get_timestamp()
                    })
                    logger.error(f"Failed to analyze: {case_title}")

            except Exception as e:
                logger.error(f"Error analyzing {case_title}: {e}")
                results.append({
                    'success': False,
                    'case_title': case_title,
                    'error': str(e),
                    'timestamp': self._get_timestamp()
                })

        successful = len([r for r in results if r['success']])
        failed = len([r for r in results if not r['success']])

        logger.info(f"Batch analysis completed. {successful} successful, {failed} failed")
        return results

    def get_analysis_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary of analysis results.

        Args:
            results: List of analysis results

        Returns:
            Summary statistics and overview
        """
        total_cases = len(results)
        successful_cases = len([r for r in results if r['success']])
        failed_cases = total_cases - successful_cases

        # Extract metadata from successful cases
        metadata_list = []
        for result in results:
            if result['success'] and 'analysis' in result:
                analysis = result['analysis']
                if 'metadata' in analysis:
                    metadata = analysis['metadata']
                    if isinstance(metadata, dict):
                        metadata_list.append(metadata)

        # Calculate statistics
        summary = {
            'total_cases': total_cases,
            'successful_cases': successful_cases,
            'failed_cases': failed_cases,
            'success_rate': (successful_cases / total_cases * 100) if total_cases > 0 else 0,
            'metadata_extracted': len(metadata_list),
            'timestamp': self._get_timestamp()
        }

        # Add case titles
        summary['successful_case_titles'] = [
            r['case_title'] for r in results if r['success']
        ]
        summary['failed_case_titles'] = [
            r['case_title'] for r in results if not r['success']
        ]

        logger.info(f"Analysis summary: {successful_cases}/{total_cases} successful ({summary['success_rate']:.1f}%)")
        return summary

    def export_analysis_results(self, results: List[Dict[str, Any]],
                               output_file: str = "results/comprehensive_analysis.json") -> str:
        """
        Export analysis results to JSON file.

        Args:
            results: List of analysis results
            output_file: Path to output file

        Returns:
            Path to exported file
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        export_data = {
            'analysis_summary': self.get_analysis_summary(results),
            'detailed_results': results,
            'export_timestamp': self._get_timestamp()
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Analysis results exported to: {output_path}")
        return str(output_path)

    def _generate_cache_key(self, case_title: str, pdf_path: str) -> str:
        """
        Generate a unique cache key for a case.

        Args:
            case_title: Title of the case
            pdf_path: Path to the PDF file

        Returns:
            Unique cache key
        """
        import hashlib
        key_string = f"{case_title}_{pdf_path}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def _save_detailed_results(self, result: Dict[str, Any]) -> None:
        """
        Save detailed analysis results to file.

        Args:
            result: Analysis result to save
        """
        try:
            if result['success'] and 'analysis' in result:
                analysis = result['analysis']
                if 'analyses' in analysis:
                    # Save individual analysis components
                    for analysis_type, analysis_result in analysis['analyses'].items():
                        if analysis_result.get('success'):
                            self.pdf_analyzer.save_analysis_results(
                                analysis_result,
                                f"results/{analysis_type}"
                            )
        except Exception as e:
            logger.warning(f"Failed to save detailed results: {e}")

    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")