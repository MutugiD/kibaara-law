"""
PDF Analyzer Module

This module handles the analysis of processed PDF content and extraction of insights.
"""

import json
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
from loguru import logger

from ..prompt_services.pleadings_prompts import PleadingsPrompts
from ..prompt_services.rulings_prompts import RulingsPrompts
from ..prompt_services.summary_prompts import SummaryPrompts
from ..services.llm_service import LLMService


class PDFAnalyzer:
    """
    Service for analyzing processed PDF content and extracting legal insights.

    This service provides functionality to analyze PDF content using specialized
    prompts and extract structured legal information.
    """

    def __init__(self, llm_service: Optional[LLMService] = None, openai_api_key: Optional[str] = None):
        """
        Initialize the PDF analyzer.

        Args:
            llm_service: LLM service for analysis (optional)
            openai_api_key: OpenAI API key (required if llm_service is not provided)
        """
        if llm_service:
            self.llm_service = llm_service
        else:
            if openai_api_key is None:
                import os
                openai_api_key = os.getenv('OPENAI_API_KEY')
            self.llm_service = LLMService(openai_api_key)
        self.pleadings_prompts = PleadingsPrompts()
        self.rulings_prompts = RulingsPrompts()
        self.summary_prompts = SummaryPrompts()

        logger.info("PDF Analyzer initialized")

    async def analyze_pleadings(self, case_title: str, pdf_content: str) -> Dict[str, Any]:
        """
        Analyze pleadings from PDF content.

        Args:
            case_title: Title of the case
            pdf_content: Processed PDF content

        Returns:
            Analysis results for pleadings
        """
        logger.info(f"Analyzing pleadings for case: {case_title}")

        try:
            # Get comprehensive pleadings prompt
            prompt = self.pleadings_prompts.get_comprehensive_pleadings_prompt(
                case_title, pdf_content
            )

            # Analyze with LLM
            response = await self.llm_service.analyze_with_gpt4o(prompt)

            if response:
                result = {
                    'success': True,
                    'case_title': case_title,
                    'analysis_type': 'pleadings',
                    'analysis': response,
                    'timestamp': self._get_timestamp()
                }
                logger.info(f"Successfully analyzed pleadings for: {case_title}")
                return result
            else:
                logger.error(f"Failed to analyze pleadings for: {case_title}")
                return {
                    'success': False,
                    'case_title': case_title,
                    'error': 'LLM analysis failed',
                    'timestamp': self._get_timestamp()
                }

        except Exception as e:
            logger.error(f"Error analyzing pleadings for {case_title}: {e}")
            return {
                'success': False,
                'case_title': case_title,
                'error': str(e),
                'timestamp': self._get_timestamp()
            }

    async def analyze_trial_decision(self, case_title: str, pdf_content: str) -> Dict[str, Any]:
        """
        Analyze trial court decision from PDF content.

        Args:
            case_title: Title of the case
            pdf_content: Processed PDF content

        Returns:
            Analysis results for trial decision
        """
        logger.info(f"Analyzing trial decision for case: {case_title}")

        try:
            # Get trial court decision prompt
            prompt = self.rulings_prompts.get_trial_court_decision_prompt(
                case_title, pdf_content
            )

            # Analyze with LLM
            response = await self.llm_service.analyze_with_gpt4o(prompt)

            if response:
                result = {
                    'success': True,
                    'case_title': case_title,
                    'analysis_type': 'trial_decision',
                    'analysis': response,
                    'timestamp': self._get_timestamp()
                }
                logger.info(f"Successfully analyzed trial decision for: {case_title}")
                return result
            else:
                logger.error(f"Failed to analyze trial decision for: {case_title}")
                return {
                    'success': False,
                    'case_title': case_title,
                    'error': 'LLM analysis failed',
                    'timestamp': self._get_timestamp()
                }

        except Exception as e:
            logger.error(f"Error analyzing trial decision for {case_title}: {e}")
            return {
                'success': False,
                'case_title': case_title,
                'error': str(e),
                'timestamp': self._get_timestamp()
            }

    async def analyze_appellate_ruling(self, case_title: str, pdf_content: str) -> Dict[str, Any]:
        """
        Analyze appellate court ruling from PDF content.

        Args:
            case_title: Title of the case
            pdf_content: Processed PDF content

        Returns:
            Analysis results for appellate ruling
        """
        logger.info(f"Analyzing appellate ruling for case: {case_title}")

        try:
            # Get appellate court ruling prompt
            prompt = self.rulings_prompts.get_appellate_court_ruling_prompt(
                case_title, pdf_content
            )

            # Analyze with LLM
            response = await self.llm_service.analyze_with_gpt4o(prompt)

            if response:
                result = {
                    'success': True,
                    'case_title': case_title,
                    'analysis_type': 'appellate_ruling',
                    'analysis': response,
                    'timestamp': self._get_timestamp()
                }
                logger.info(f"Successfully analyzed appellate ruling for: {case_title}")
                return result
            else:
                logger.error(f"Failed to analyze appellate ruling for: {case_title}")
                return {
                    'success': False,
                    'case_title': case_title,
                    'error': 'LLM analysis failed',
                    'timestamp': self._get_timestamp()
                }

        except Exception as e:
            logger.error(f"Error analyzing appellate ruling for {case_title}: {e}")
            return {
                'success': False,
                'case_title': case_title,
                'error': str(e),
                'timestamp': self._get_timestamp()
            }

    async def create_comprehensive_summary(self, case_title: str, pleadings_analysis: str,
                                   trial_decision: str, appellate_ruling: str) -> Dict[str, Any]:
        """
        Create comprehensive case summary from all analyses.

        Args:
            case_title: Title of the case
            pleadings_analysis: Analysis of pleadings
            trial_decision: Analysis of trial decision
            appellate_ruling: Analysis of appellate ruling

        Returns:
            Comprehensive summary results
        """
        logger.info(f"Creating comprehensive summary for case: {case_title}")

        try:
            # Get comprehensive summary prompt
            prompt = self.summary_prompts.get_comprehensive_case_summary_prompt(
                case_title, pleadings_analysis, trial_decision, appellate_ruling
            )

            # Analyze with LLM
            response = await self.llm_service.analyze_with_gpt4o(prompt)

            if response:
                result = {
                    'success': True,
                    'case_title': case_title,
                    'analysis_type': 'comprehensive_summary',
                    'summary': response,
                    'timestamp': self._get_timestamp()
                }
                logger.info(f"Successfully created comprehensive summary for: {case_title}")
                return result
            else:
                logger.error(f"Failed to create comprehensive summary for: {case_title}")
                return {
                    'success': False,
                    'case_title': case_title,
                    'error': 'LLM analysis failed',
                    'timestamp': self._get_timestamp()
                }

        except Exception as e:
            logger.error(f"Error creating comprehensive summary for {case_title}: {e}")
            return {
                'success': False,
                'case_title': case_title,
                'error': str(e),
                'timestamp': self._get_timestamp()
            }

    async def extract_metadata(self, case_title: str, comprehensive_summary: str) -> Dict[str, Any]:
        """
        Extract structured metadata from comprehensive summary.

        Args:
            case_title: Title of the case
            comprehensive_summary: Comprehensive case summary

        Returns:
            Structured metadata
        """
        logger.info(f"Extracting metadata for case: {case_title}")

        try:
            # Get metadata extraction prompt
            prompt = self.summary_prompts.get_case_metadata_extraction_prompt(
                case_title, comprehensive_summary
            )

            # Analyze with LLM
            response = await self.llm_service.analyze_with_gpt4o(prompt)

            if response:
                # Try to parse JSON from response
                metadata = self._extract_json_from_text(response)

                result = {
                    'success': True,
                    'case_title': case_title,
                    'analysis_type': 'metadata_extraction',
                    'metadata': metadata,
                    'raw_response': response,
                    'timestamp': self._get_timestamp()
                }
                logger.info(f"Successfully extracted metadata for: {case_title}")
                return result
            else:
                logger.error(f"Failed to extract metadata for: {case_title}")
                return {
                    'success': False,
                    'case_title': case_title,
                    'error': 'LLM analysis failed',
                    'timestamp': self._get_timestamp()
                }

        except Exception as e:
            logger.error(f"Error extracting metadata for {case_title}: {e}")
            return {
                'success': False,
                'case_title': case_title,
                'error': str(e),
                'timestamp': self._get_timestamp()
            }

    async def analyze_case_complete(self, case_title: str, pdf_content: str) -> Dict[str, Any]:
        """
        Perform complete analysis of a case including all aspects.

        Args:
            case_title: Title of the case
            pdf_content: Processed PDF content

        Returns:
            Complete analysis results
        """
        logger.info(f"Starting complete analysis for case: {case_title}")

        results = {
            'case_title': case_title,
            'analysis_timestamp': self._get_timestamp(),
            'success': True,
            'analyses': {}
        }

        try:
            # Analyze pleadings
            pleadings_result = await self.analyze_pleadings(case_title, pdf_content)
            results['analyses']['pleadings'] = pleadings_result

            if not pleadings_result['success']:
                results['success'] = False
                results['error'] = 'Pleadings analysis failed'
                return results

            # Analyze trial decision
            trial_result = await self.analyze_trial_decision(case_title, pdf_content)
            results['analyses']['trial_decision'] = trial_result

            if not trial_result['success']:
                results['success'] = False
                results['error'] = 'Trial decision analysis failed'
                return results

            # Analyze appellate ruling
            appellate_result = await self.analyze_appellate_ruling(case_title, pdf_content)
            results['analyses']['appellate_ruling'] = appellate_result

            if not appellate_result['success']:
                results['success'] = False
                results['error'] = 'Appellate ruling analysis failed'
                return results

            # Create comprehensive summary
            pleadings_text = pleadings_result.get('analysis', '')
            trial_text = trial_result.get('analysis', '')
            appellate_text = appellate_result.get('analysis', '')

            summary_result = await self.create_comprehensive_summary(
                case_title, pleadings_text, trial_text, appellate_text
            )
            results['analyses']['comprehensive_summary'] = summary_result

            if not summary_result['success']:
                results['success'] = False
                results['error'] = 'Comprehensive summary creation failed'
                return results

            # Extract metadata
            summary_text = summary_result.get('summary', '')
            metadata_result = await self.extract_metadata(case_title, summary_text)
            results['analyses']['metadata'] = metadata_result

            if not metadata_result['success']:
                results['success'] = False
                results['error'] = 'Metadata extraction failed'
                return results

            logger.info(f"Successfully completed analysis for: {case_title}")
            return results

        except Exception as e:
            logger.error(f"Error in complete analysis for {case_title}: {e}")
            results['success'] = False
            results['error'] = str(e)
            return results

    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from text response.

        Args:
            text: Text containing JSON

        Returns:
            Parsed JSON dictionary
        """
        try:
            # Look for JSON pattern in text
            json_pattern = r'\{.*\}'
            json_match = re.search(json_pattern, text, re.DOTALL)

            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                # If no JSON found, return structured text
                return {
                    'raw_text': text,
                    'parsing_status': 'no_json_found'
                }

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from text: {e}")
            return {
                'raw_text': text,
                'parsing_status': 'json_decode_error',
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error extracting JSON: {e}")
            return {
                'raw_text': text,
                'parsing_status': 'extraction_error',
                'error': str(e)
            }

    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def save_analysis_results(self, results: Dict[str, Any], output_dir: str = "results") -> str:
        """
        Save analysis results to file.

        Args:
            results: Analysis results to save
            output_dir: Directory to save results

        Returns:
            Path to saved file
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        case_title = results.get('case_title', 'unknown_case')
        safe_title = re.sub(r'[^\w\s-]', '', case_title)
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        safe_title = safe_title.strip('-')

        timestamp = results.get('analysis_timestamp', self._get_timestamp()).replace(' ', '_').replace(':', '-')
        filename = f"{safe_title}_analysis_{timestamp}.json"

        filepath = output_path / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"Analysis results saved to: {filepath}")
        return str(filepath)