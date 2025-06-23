"""
Result formatter service for formatting analysis results.

This module formats case analysis results according to user requirements
and provides various output formats for the legal assistant.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from loguru import logger

from ..models.result_models import PromptResponse, AnalysisResult
from ..models.case_models import Case


class ResultFormatter:
    """
    Service for formatting case analysis results.

    This service formats analysis results according to user requirements
    and provides various output formats for different use cases.
    """

    def __init__(self) -> None:
        """Initialize the result formatter."""
        self.supported_formats = ["json", "text", "summary", "detailed"]

    def format_response(self, response: PromptResponse, format_type: str = "json") -> str:
        """
        Format a prompt response according to specified format.

        Args:
            response: The prompt response to format
            format_type: The desired output format

        Returns:
            Formatted response as string
        """
        logger.info(f"Formatting response in {format_type} format")

        if format_type == "json":
            return self._format_json(response)
        elif format_type == "text":
            return self._format_text(response)
        elif format_type == "summary":
            return self._format_summary(response)
        elif format_type == "detailed":
            return self._format_detailed(response)
        else:
            logger.warning(f"Unsupported format type: {format_type}, using JSON")
            return self._format_json(response)

    def _format_json(self, response: PromptResponse) -> str:
        """Format response as JSON."""
        try:
            # Convert response to dictionary
            response_dict = {
                "prompt_id": response.prompt_id,
                "original_prompt": response.original_prompt,
                "search_criteria": response.search_criteria,
                "status": response.status,
                "processing_time": response.processing_time,
                "statistics": response.get_statistics(),
                "cases": []
            }

            # Add case data
            for analysis_result in response.analyzed_cases:
                case_dict = self._case_to_dict(analysis_result.case)
                case_dict["analysis"] = {
                    "confidence_score": analysis_result.confidence_score,
                    "processing_time": analysis_result.processing_time,
                    "extraction_notes": analysis_result.extraction_notes,
                    "quality_indicators": analysis_result.quality_indicators
                }
                response_dict["cases"].append(case_dict)

            # Add error information if any
            if response.error_message:
                response_dict["error"] = response.error_message

            return json.dumps(response_dict, indent=2, default=str)

        except Exception as e:
            logger.error(f"Failed to format JSON response: {str(e)}")
            return json.dumps({"error": f"Failed to format response: {str(e)}"})

    def _format_text(self, response: PromptResponse) -> str:
        """Format response as human-readable text."""
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append("LEGAL CASE ANALYSIS RESULTS")
        lines.append("=" * 80)
        lines.append("")

        # Original prompt
        lines.append("ORIGINAL PROMPT:")
        lines.append(response.original_prompt)
        lines.append("")

        # Statistics
        stats = response.get_statistics()
        lines.append("ANALYSIS STATISTICS:")
        lines.append(f"  Total cases found: {stats['total_cases']}")
        lines.append(f"  Multi-hop cases: {stats['multi_hop_cases']}")
        lines.append(f"  Single-hop cases: {stats['single_hop_cases']}")
        lines.append(f"  Average confidence: {stats['average_confidence']:.2f}")
        lines.append(f"  Processing time: {stats['processing_time']:.2f} seconds")
        lines.append("")

        # Court level distribution
        if stats.get('court_level_distribution'):
            lines.append("COURT LEVEL DISTRIBUTION:")
            for level, count in stats['court_level_distribution'].items():
                lines.append(f"  {level}: {count} cases")
            lines.append("")

        # Case details
        lines.append("CASE DETAILS:")
        lines.append("-" * 80)

        for i, analysis_result in enumerate(response.analyzed_cases, 1):
            case = analysis_result.case
            lines.append(f"")
            lines.append(f"CASE {i}: {case.metadata.case_title}")
            lines.append(f"Confidence Score: {analysis_result.confidence_score:.2f}")
            lines.append(f"Processing Time: {analysis_result.processing_time:.2f}s")

            # Basic case information
            if case.metadata.citation:
                lines.append(f"Citation: {case.metadata.citation}")
            if case.metadata.parties:
                lines.append(f"Parties: {' v '.join(case.metadata.parties)}")
            if case.metadata.subject_matter:
                lines.append(f"Subject Matter: {case.metadata.subject_matter}")

            # Litigation hops
            if case.litigation_hops:
                lines.append(f"Litigation Hops ({len(case.litigation_hops)}):")
                for j, hop in enumerate(case.litigation_hops, 1):
                    lines.append(f"  {j}. {hop.court_level.value} - {hop.case_number}")
                    if hop.status:
                        lines.append(f"     Status: {hop.status.value}")
                    if hop.outcome:
                        lines.append(f"     Outcome: {hop.outcome}")

            # Content summary
            if case.pleadings:
                pleadings_preview = case.pleadings[:200] + "..." if len(case.pleadings) > 200 else case.pleadings
                lines.append(f"Pleadings Preview: {pleadings_preview}")

            if case.decisions:
                decisions_preview = case.decisions[:200] + "..." if len(case.decisions) > 200 else case.decisions
                lines.append(f"Decisions Preview: {decisions_preview}")

            # Quality indicators
            if analysis_result.quality_indicators:
                lines.append("Quality Indicators:")
                for indicator_type, data in analysis_result.quality_indicators.items():
                    if isinstance(data, dict) and "confidence" in data:
                        lines.append(f"  {indicator_type}: {data['confidence']:.2f}")

            lines.append("-" * 80)

        # Error information
        if response.error_message:
            lines.append("")
            lines.append("ERRORS:")
            lines.append(response.error_message)

        return "\n".join(lines)

    def _format_summary(self, response: PromptResponse) -> str:
        """Format response as a concise summary."""
        lines = []

        # Summary header
        lines.append("LEGAL CASE ANALYSIS SUMMARY")
        lines.append("=" * 50)
        lines.append("")

        # Key statistics
        stats = response.get_statistics()
        lines.append(f"Found {stats['total_cases']} cases matching your criteria")
        lines.append(f"Multi-hop cases: {stats['multi_hop_cases']}")
        lines.append(f"Average confidence: {stats['average_confidence']:.2f}")
        lines.append(f"Processing time: {stats['processing_time']:.2f} seconds")
        lines.append("")

        # Case list
        lines.append("CASES FOUND:")
        for i, analysis_result in enumerate(response.analyzed_cases, 1):
            case = analysis_result.case
            confidence = analysis_result.confidence_score

            # Create a concise case description
            case_desc = f"{i}. {case.metadata.case_title}"
            if case.metadata.citation:
                case_desc += f" ({case.metadata.citation})"

            # Add litigation hop information
            if case.litigation_hops:
                hop_desc = f" - {len(case.litigation_hops)} hop(s): "
                hop_levels = [hop.court_level.value for hop in case.litigation_hops]
                case_desc += hop_desc + " → ".join(hop_levels)

            # Add confidence indicator
            if confidence >= 0.8:
                confidence_indicator = "✓"
            elif confidence >= 0.6:
                confidence_indicator = "~"
            else:
                confidence_indicator = "?"

            case_desc += f" [{confidence_indicator}]"
            lines.append(case_desc)

        # Quality summary
        high_quality = sum(1 for r in response.analyzed_cases if r.confidence_score >= 0.8)
        medium_quality = sum(1 for r in response.analyzed_cases if 0.6 <= r.confidence_score < 0.8)
        low_quality = sum(1 for r in response.analyzed_cases if r.confidence_score < 0.6)

        lines.append("")
        lines.append("QUALITY SUMMARY:")
        lines.append(f"  High quality (≥0.8): {high_quality} cases")
        lines.append(f"  Medium quality (0.6-0.8): {medium_quality} cases")
        lines.append(f"  Low quality (<0.6): {low_quality} cases")

        return "\n".join(lines)

    def _format_detailed(self, response: PromptResponse) -> str:
        """Format response with maximum detail."""
        lines = []

        # Detailed header
        lines.append("DETAILED LEGAL CASE ANALYSIS")
        lines.append("=" * 80)
        lines.append("")

        # Original prompt and criteria
        lines.append("ORIGINAL PROMPT:")
        lines.append(response.original_prompt)
        lines.append("")

        lines.append("EXTRACTED SEARCH CRITERIA:")
        criteria = response.search_criteria
        lines.append(f"  Case count: {criteria.get('case_count', 'Not specified')}")
        lines.append(f"  Court levels: {criteria.get('court_levels', 'Not specified')}")
        lines.append(f"  Subject matter: {criteria.get('subject_matter', 'Not specified')}")
        lines.append(f"  Case type: {criteria.get('case_type', 'Not specified')}")
        lines.append(f"  Keywords: {criteria.get('keywords', 'Not specified')}")
        lines.append(f"  Require multi-hop: {criteria.get('require_multi_hop', 'Not specified')}")
        lines.append(f"  Minimum hops: {criteria.get('min_hops', 'Not specified')}")
        lines.append("")

        # Processing information
        lines.append("PROCESSING INFORMATION:")
        lines.append(f"  Status: {response.status}")
        lines.append(f"  Processing time: {response.processing_time:.2f} seconds")
        lines.append(f"  Search results: {len(response.search_results)}")
        lines.append(f"  Analyzed cases: {len(response.analyzed_cases)}")
        lines.append("")

        # Detailed case analysis
        lines.append("DETAILED CASE ANALYSIS:")
        lines.append("=" * 80)

        for i, analysis_result in enumerate(response.analyzed_cases, 1):
            case = analysis_result.case
            lines.append(f"")
            lines.append(f"CASE {i}: {case.metadata.case_title}")
            lines.append("-" * 60)

            # Metadata
            lines.append("METADATA:")
            lines.append(f"  Citation: {case.metadata.citation or 'Not available'}")
            lines.append(f"  Parties: {', '.join(case.metadata.parties) if case.metadata.parties else 'Not available'}")
            lines.append(f"  Subject Matter: {case.metadata.subject_matter or 'Not available'}")
            lines.append(f"  Case Type: {case.metadata.case_type or 'Not available'}")
            lines.append(f"  Filing Date: {case.metadata.filing_date or 'Not available'}")
            lines.append(f"  Source URL: {case.metadata.source_url or 'Not available'}")

            # Analysis metrics
            lines.append("")
            lines.append("ANALYSIS METRICS:")
            lines.append(f"  Confidence Score: {analysis_result.confidence_score:.3f}")
            lines.append(f"  Processing Time: {analysis_result.processing_time:.3f} seconds")
            lines.append(f"  Analysis Timestamp: {analysis_result.analysis_timestamp}")

            # Quality indicators
            if analysis_result.quality_indicators:
                lines.append("")
                lines.append("QUALITY INDICATORS:")
                for indicator_type, data in analysis_result.quality_indicators.items():
                    if isinstance(data, dict):
                        lines.append(f"  {indicator_type.upper()}:")
                        for key, value in data.items():
                            if isinstance(value, (int, float)):
                                lines.append(f"    {key}: {value:.3f}" if isinstance(value, float) else f"    {key}: {value}")
                            else:
                                lines.append(f"    {key}: {value}")

            # Litigation hops
            if case.litigation_hops:
                lines.append("")
                lines.append("LITIGATION HOPS:")
                for j, hop in enumerate(case.litigation_hops, 1):
                    lines.append(f"  Hop {j}:")
                    lines.append(f"    Court Level: {hop.court_level.value}")
                    lines.append(f"    Case Number: {hop.case_number}")
                    lines.append(f"    Status: {hop.status.value}")
                    lines.append(f"    Filing Date: {hop.filing_date or 'Not available'}")
                    lines.append(f"    Decision Date: {hop.decision_date or 'Not available'}")
                    lines.append(f"    Judge: {hop.judge or 'Not available'}")
                    lines.append(f"    Court Location: {hop.court_location or 'Not available'}")
                    if hop.outcome:
                        lines.append(f"    Outcome: {hop.outcome}")

            # Content
            if case.pleadings:
                lines.append("")
                lines.append("PLEADINGS:")
                lines.append(case.pleadings)

            if case.decisions:
                lines.append("")
                lines.append("DECISIONS:")
                lines.append(case.decisions)

            # Documents
            if case.documents:
                lines.append("")
                lines.append("DOCUMENTS:")
                for doc_type, content in case.documents.items():
                    lines.append(f"  {doc_type.upper()}:")
                    lines.append(f"    Length: {len(content)} characters")
                    lines.append(f"    Preview: {content[:200]}...")

            # Extraction notes
            if analysis_result.extraction_notes:
                lines.append("")
                lines.append("EXTRACTION NOTES:")
                for note in analysis_result.extraction_notes:
                    lines.append(f"  - {note}")

            lines.append("=" * 80)

        # Error information
        if response.error_message:
            lines.append("")
            lines.append("ERRORS:")
            lines.append(response.error_message)

        return "\n".join(lines)

    def _case_to_dict(self, case: Case) -> Dict[str, Any]:
        """Convert a case object to dictionary for JSON serialization."""
        return {
            "metadata": {
                "case_title": case.metadata.case_title,
                "citation": case.metadata.citation,
                "parties": case.metadata.parties,
                "subject_matter": case.metadata.subject_matter,
                "case_type": case.metadata.case_type,
                "filing_date": case.metadata.filing_date,
                "source_url": case.metadata.source_url,
                "last_updated": case.metadata.last_updated
            },
            "litigation_hops": [
                {
                    "court_level": hop.court_level.value,
                    "case_number": hop.case_number,
                    "filing_date": hop.filing_date,
                    "decision_date": hop.decision_date,
                    "status": hop.status.value,
                    "outcome": hop.outcome,
                    "judge": hop.judge,
                    "court_location": hop.court_location
                }
                for hop in case.litigation_hops
            ],
            "pleadings": case.pleadings,
            "decisions": case.decisions,
            "documents": case.documents,
            "related_cases": case.related_cases,
            "tags": case.tags,
            "analysis_notes": case.analysis_notes,
            "is_multi_hop": case.is_multi_hop,
            "current_court_level": case.current_court_level.value if case.current_court_level else None,
            "case_number": case.case_number
        }

    def create_prompt_response(self, prompt_id: str, original_prompt: str,
                             search_criteria: Dict[str, Any], search_results: List[Any],
                             analyzed_cases: List[AnalysisResult], processing_time: float,
                             error_message: Optional[str] = None) -> PromptResponse:
        """
        Create a prompt response object.

        Args:
            prompt_id: Unique identifier for the prompt
            original_prompt: The original user prompt
            search_criteria: Extracted search criteria
            search_results: Initial search results
            analyzed_cases: Analyzed case results
            processing_time: Total processing time
            error_message: Optional error message

        Returns:
            PromptResponse object
        """
        return PromptResponse(
            prompt_id=prompt_id,
            original_prompt=original_prompt,
            search_criteria=search_criteria,
            search_results=search_results,
            analyzed_cases=analyzed_cases,
            processing_time=processing_time,
            status="completed" if not error_message else "error",
            error_message=error_message
        )

    def format_results(self, analysis_results: List[Dict[str, Any]]) -> str:
        """
        Format analysis results into a comprehensive text report.

        Args:
            analysis_results: List of analysis results

        Returns:
            Formatted text report
        """
        logger.info("Formatting analysis results...")

        # Create comprehensive report
        report = []
        report.append("=" * 100)
        report.append("KENYAN COURT CASES ANALYSIS REPORT")
        report.append("=" * 100)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Cases Analyzed: {len(analysis_results)}")
        report.append("=" * 100)
        report.append("")

        if not analysis_results:
            report.append("NO CASES FOUND WITH 2-HOP LITIGATION")
            report.append("")
            report.append("This could be due to:")
            report.append("- Search results not containing sufficient 2-hop litigation information")
            report.append("- LLM analysis not extracting proper trial/appellate court data")
            report.append("- Filtering criteria being too strict")
            report.append("")
            report.append("Check the following files for debugging:")
            report.append("- results/parsed_llm_analysis.json (LLM output)")
            report.append("- results/two_hop_filtering_results.json (Filtering details)")
            report.append("- results/gpt_serp_analysis_response.txt (Raw LLM response)")
            report.append("- logs/legal_assistant.log (Complete workflow logs)")
            report.append("")
        else:
            # Add detailed case information
            for i, result in enumerate(analysis_results, 1):
                report.append(f"CASE {i}:")
                report.append("-" * 50)

                # Basic case info
                report.append(f"Title: {result.get('title', 'Unknown')}")
                report.append(f"Description: {result.get('description', 'No description available')}")
                report.append(f"Confidence: {result.get('confidence', 'Unknown')}")
                report.append("")

                # Trial court info
                trial_court = result.get('trial_court', {})
                report.append("TRIAL COURT:")
                report.append(f"  Court: {trial_court.get('court', 'Unknown')}")
                report.append(f"  Case Number: {trial_court.get('case_number', 'Unknown')}")
                report.append(f"  Date: {trial_court.get('date', 'Unknown')}")
                report.append(f"  URL: {trial_court.get('url', 'Unknown')}")
                report.append("")

                # Appellate court info
                appellate_court = result.get('appellate_court', {})
                report.append("APPELLATE COURT:")
                report.append(f"  Court: {appellate_court.get('court', 'Unknown')}")
                report.append(f"  Case Number: {appellate_court.get('case_number', 'Unknown')}")
                report.append(f"  Date: {appellate_court.get('date', 'Unknown')}")
                report.append(f"  URL: {appellate_court.get('url', 'Unknown')}")
                report.append("")
                report.append("")

        # Add debugging information
        report.append("=" * 100)
        report.append("DEBUGGING INFORMATION")
        report.append("=" * 100)
        report.append("")
        report.append("For detailed debugging, check these files:")
        report.append("")
        report.append("1. results/parsed_llm_analysis.json")
        report.append("   - Complete LLM analysis output")
        report.append("   - All cases found by GPT-4o")
        report.append("")
        report.append("2. results/two_hop_filtering_results.json")
        report.append("   - Detailed filtering process")
        report.append("   - Why cases were accepted/rejected")
        report.append("")
        report.append("3. results/gpt_serp_analysis_response.txt")
        report.append("   - Raw GPT-4o response")
        report.append("   - Original LLM output before parsing")
        report.append("")
        report.append("4. logs/legal_assistant.log")
        report.append("   - Complete workflow execution log")
        report.append("   - Step-by-step process details")
        report.append("")

        # Add JSON summary
        report.append("=" * 100)
        report.append("JSON SUMMARY")
        report.append("=" * 100)
        report.append("")

        summary_data = {
            "timestamp": datetime.now().isoformat(),
            "total_cases_found": len(analysis_results),
            "cases": analysis_results,
            "workflow_status": "completed" if analysis_results else "no_cases_found"
        }

        report.append(json.dumps(summary_data, indent=2, ensure_ascii=False))

        return "\n".join(report)

    def format_for_file(self, results: Dict[str, Any]) -> str:
        """
        Format results for file output.

        Args:
            results: Results dictionary

        Returns:
            Formatted string for file output
        """
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append("LEGAL CASE ANALYSIS RESULTS")
        lines.append("=" * 80)
        lines.append("")

        # Original prompt
        lines.append("ORIGINAL PROMPT:")
        lines.append(results.get("original_prompt", ""))
        lines.append("")

        # Statistics
        stats = results.get("analysis_statistics", {})
        lines.append("ANALYSIS STATISTICS:")
        lines.append(f"  Total cases found: {stats.get('total_cases_found', 0)}")
        lines.append(f"  Multi-hop cases: {stats.get('multi_hop_cases', 0)}")
        lines.append(f"  Single-hop cases: {stats.get('single_hop_cases', 0)}")
        lines.append(f"  Average confidence: {stats.get('average_confidence', 0.0):.2f}")
        lines.append(f"  Processing time: {stats.get('processing_time', 0.0):.2f} seconds")
        lines.append("")

        # Case details
        lines.append("CASE DETAILS:")
        lines.append("-" * 80)

        for i, case in enumerate(results.get("case_details", []), 1):
            lines.append(f"")
            lines.append(f"CASE {i}: {case.get('title', 'Unknown')}")
            lines.append(f"URL: {case.get('url', 'Unknown')}")
            lines.append(f"Case Type: {case.get('case_type', 'Unknown')}")

            # LLM Analysis
            llm_analysis = case.get('llm_analysis', {})
            if llm_analysis:
                analysis_text = llm_analysis.get('analysis_text', '')
                if analysis_text:
                    lines.append("ANALYSIS:")
                    lines.append(analysis_text[:1000] + "..." if len(analysis_text) > 1000 else analysis_text)

            # Litigation hops
            hops = case.get('litigation_hops', [])
            if hops:
                lines.append(f"LITIGATION HOPS ({len(hops)}):")
                for j, hop in enumerate(hops, 1):
                    lines.append(f"  {j}. {hop}")

            lines.append("-" * 80)

        # Errors
        errors = results.get("errors", [])
        if errors:
            lines.append("")
            lines.append("ERRORS:")
            for error in errors:
                lines.append(f"  - {error}")

        return "\n".join(lines)