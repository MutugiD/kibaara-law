"""
Case analyzer service for processing downloaded cases and extracting insights.

This module analyzes downloaded legal cases to extract structured information,
identify litigation patterns, and generate insights.
"""

import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger

from ..models.case_models import Case, LitigationHop, CourtLevel, CaseStatus
from ..models.result_models import AnalysisResult


class CaseAnalyzer:
    """
    Service for analyzing legal cases and extracting insights.

    This service processes downloaded cases to extract structured information,
    identify litigation patterns, and generate comprehensive analysis results.
    """

    def __init__(self, openai_api_key: Optional[str] = None) -> None:
        """
        Initialize the case analyzer.

        Args:
            openai_api_key: Optional OpenAI API key for LLM integration
        """
        self.openai_api_key = openai_api_key
        self.confidence_thresholds = {
            "metadata": 0.8,
            "litigation_hops": 0.7,
            "pleadings": 0.6,
            "decisions": 0.7,
            "documents": 0.5
        }

    async def analyze_case(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single case and extract insights.

        Args:
            case: The case dictionary to analyze

        Returns:
            Analysis result dictionary
        """
        case_title = case.get('title', 'Unknown Case')
        logger.info(f"Analyzing case: {case_title}")

        start_time = datetime.now()

        try:
            # Extract basic information
            appellate_court = case.get('appellate_court', {})
            trial_reference = case.get('trial_reference', {})
            appellate_doc = case.get('appellate_document', {})

            # Create analysis result
            analysis_result = {
                "case_title": case_title,
                "appellate_court": appellate_court,
                "trial_reference": trial_reference,
                "appellate_document": appellate_doc,
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "confidence_score": 0.8,  # Default confidence
                "extraction_notes": [
                    f"Successfully analyzed case: {case_title}",
                    f"Appellate court: {appellate_court.get('court', 'Unknown')}",
                    f"Trial reference: {trial_reference.get('court', 'Unknown')}",
                    f"Document downloaded: {'Yes' if appellate_doc else 'No'}"
                ],
                "quality_indicators": {
                    "has_appellate_info": bool(appellate_court.get('court')),
                    "has_trial_reference": bool(trial_reference.get('court')),
                    "has_document": bool(appellate_doc),
                    "is_2_hop": True  # All cases passed 2-hop filter
                }
            }

            logger.info(f"Case analysis completed for: {case_title}")
            return analysis_result

        except Exception as e:
            logger.error(f"Failed to analyze case: {str(e)}")
            # Return a basic analysis result with error information
            processing_time = (datetime.now() - start_time).total_seconds()
            return {
                "case_title": case_title,
                "processing_time": processing_time,
                "confidence_score": 0.0,
                "extraction_notes": [f"Analysis failed: {str(e)}"],
                "quality_indicators": {"error": str(e)}
            }

    def _analyze_metadata_quality(self, case: Case) -> Dict[str, Any]:
        """Analyze the quality of case metadata."""
        quality_score = 0.0
        issues = []
        strengths = []

        # Check required fields
        if case.metadata.case_title:
            quality_score += 0.3
            strengths.append("Case title present")
        else:
            issues.append("Missing case title")

        if case.metadata.parties and len(case.metadata.parties) >= 2:
            quality_score += 0.2
            strengths.append("Parties identified")
        else:
            issues.append("Insufficient party information")

        if case.metadata.citation:
            quality_score += 0.2
            strengths.append("Legal citation present")
        else:
            issues.append("Missing legal citation")

        if case.metadata.source_url:
            quality_score += 0.1
            strengths.append("Source URL available")
        else:
            issues.append("Missing source URL")

        if case.metadata.subject_matter:
            quality_score += 0.1
            strengths.append("Subject matter identified")
        else:
            issues.append("Missing subject matter")

        if case.metadata.case_type:
            quality_score += 0.1
            strengths.append("Case type identified")
        else:
            issues.append("Missing case type")

        return {
            "confidence": min(quality_score, 1.0),
            "issues": issues,
            "strengths": strengths,
            "completeness": quality_score
        }

    def _analyze_litigation_hops(self, case: Case) -> Dict[str, Any]:
        """Analyze litigation hops and progression."""
        quality_score = 0.0
        issues = []
        strengths = []

        if not case.litigation_hops:
            issues.append("No litigation hops found")
            return {
                "confidence": 0.0,
                "issues": issues,
                "strengths": strengths,
                "hop_count": 0,
                "is_multi_hop": False
            }

        hop_count = len(case.litigation_hops)
        quality_score += min(hop_count * 0.2, 0.6)  # Max 0.6 for 3+ hops
        strengths.append(f"Found {hop_count} litigation hop(s)")

        # Check for multi-hop progression
        if case.is_multi_hop:
            quality_score += 0.2
            strengths.append("Multi-hop litigation identified")
        else:
            issues.append("Single-hop litigation only")

        # Analyze hop quality
        valid_hops = 0
        for hop in case.litigation_hops:
            if hop.court_level and hop.case_number:
                valid_hops += 1
            else:
                issues.append(f"Incomplete hop data: {hop}")

        hop_quality = valid_hops / hop_count if hop_count > 0 else 0
        quality_score += hop_quality * 0.2

        # Check court level progression
        court_levels = [hop.court_level for hop in case.litigation_hops if hop.court_level]
        if len(court_levels) > 1:
            # Check if progression makes sense (e.g., Magistrate -> High Court -> Court of Appeal)
            progression_valid = self._validate_court_progression(court_levels)
            if progression_valid:
                quality_score += 0.1
                strengths.append("Valid court level progression")
            else:
                issues.append("Unusual court level progression")

        return {
            "confidence": min(quality_score, 1.0),
            "issues": issues,
            "strengths": strengths,
            "hop_count": hop_count,
            "is_multi_hop": case.is_multi_hop,
            "valid_hops": valid_hops,
            "hop_quality": hop_quality
        }

    def _validate_court_progression(self, court_levels: List[CourtLevel]) -> bool:
        """Validate that court level progression makes sense."""
        if len(court_levels) < 2:
            return True

        # Define valid progression patterns
        valid_patterns = [
            [CourtLevel.MAGISTRATE, CourtLevel.HIGH_COURT],
            [CourtLevel.HIGH_COURT, CourtLevel.COURT_OF_APPEAL],
            [CourtLevel.COURT_OF_APPEAL, CourtLevel.SUPREME_COURT],
            [CourtLevel.MAGISTRATE, CourtLevel.HIGH_COURT, CourtLevel.COURT_OF_APPEAL],
            [CourtLevel.HIGH_COURT, CourtLevel.COURT_OF_APPEAL, CourtLevel.SUPREME_COURT]
        ]

        # Check if the progression matches any valid pattern
        for pattern in valid_patterns:
            if len(court_levels) == len(pattern):
                if all(actual == expected for actual, expected in zip(court_levels, pattern)):
                    return True

        return False

    def _analyze_case_content(self, case: Case) -> Dict[str, Any]:
        """Analyze case content (pleadings, decisions)."""
        pleadings_confidence = 0.0
        decisions_confidence = 0.0
        issues = []
        strengths = []

        # Analyze pleadings
        if case.pleadings:
            pleadings_length = len(case.pleadings)
            if pleadings_length > 100:
                pleadings_confidence = 0.8
                strengths.append("Substantial pleadings content")
            elif pleadings_length > 50:
                pleadings_confidence = 0.6
                strengths.append("Moderate pleadings content")
            else:
                pleadings_confidence = 0.3
                issues.append("Limited pleadings content")
        else:
            issues.append("No pleadings found")

        # Analyze decisions
        if case.decisions:
            decisions_length = len(case.decisions)
            if decisions_length > 200:
                decisions_confidence = 0.9
                strengths.append("Comprehensive decision content")
            elif decisions_length > 100:
                decisions_confidence = 0.7
                strengths.append("Detailed decision content")
            elif decisions_length > 50:
                decisions_confidence = 0.5
                strengths.append("Basic decision content")
            else:
                decisions_confidence = 0.3
                issues.append("Limited decision content")
        else:
            issues.append("No decisions found")

        # Analyze content quality indicators
        content_indicators = self._extract_content_indicators(case)

        return {
            "pleadings_confidence": pleadings_confidence,
            "decisions_confidence": decisions_confidence,
            "issues": issues,
            "strengths": strengths,
            "content_indicators": content_indicators
        }

    def _extract_content_indicators(self, case: Case) -> Dict[str, Any]:
        """Extract quality indicators from case content."""
        indicators = {}

        # Check for legal terminology
        legal_terms = [
            "plaintiff", "defendant", "appellant", "respondent", "petitioner",
            "judgment", "ruling", "appeal", "application", "motion",
            "evidence", "testimony", "witness", "exhibit", "affidavit"
        ]

        content_text = ""
        if case.pleadings:
            content_text += case.pleadings.lower()
        if case.decisions:
            content_text += case.decisions.lower()

        legal_term_count = sum(1 for term in legal_terms if term in content_text)
        indicators["legal_terminology_density"] = legal_term_count / len(legal_terms) if legal_terms else 0

        # Check for citation patterns
        citation_patterns = [
            r'\d+\s+[A-Z]+\s+\d+',  # e.g., "2020 KLR 123"
            r'\[20\d{2}\]\s+[A-Z]+',  # e.g., "[2020] KLR"
            r'Civil\s+Case\s+No\.',  # e.g., "Civil Case No. 123"
            r'Criminal\s+Case\s+No\.'  # e.g., "Criminal Case No. 123"
        ]

        citation_count = 0
        for pattern in citation_patterns:
            citations = re.findall(pattern, content_text, re.IGNORECASE)
            citation_count += len(citations)

        indicators["citation_count"] = citation_count

        return indicators

    def _analyze_documents(self, case: Case) -> Dict[str, Any]:
        """Analyze case documents."""
        quality_score = 0.0
        issues = []
        strengths = []

        if not case.documents:
            issues.append("No documents found")
            return {
                "confidence": 0.0,
                "issues": issues,
                "strengths": strengths,
                "document_count": 0
            }

        document_count = len(case.documents)
        quality_score += min(document_count * 0.2, 0.6)  # Max 0.6 for 3+ documents
        strengths.append(f"Found {document_count} document(s)")

        # Analyze document types
        document_types = list(case.documents.keys())
        if "pleadings" in document_types:
            quality_score += 0.2
            strengths.append("Pleadings document present")
        if "judgment" in document_types or "decision" in document_types:
            quality_score += 0.2
            strengths.append("Judgment/decision document present")

        # Check document content quality
        total_content_length = sum(len(content) for content in case.documents.values())
        if total_content_length > 1000:
            quality_score += 0.1
            strengths.append("Substantial document content")
        elif total_content_length > 500:
            quality_score += 0.05
            strengths.append("Moderate document content")
        else:
            issues.append("Limited document content")

        return {
            "confidence": min(quality_score, 1.0),
            "issues": issues,
            "strengths": strengths,
            "document_count": document_count,
            "document_types": document_types,
            "total_content_length": total_content_length
        }

    def _calculate_confidence_score(self, component_scores: Dict[str, float]) -> float:
        """Calculate overall confidence score from component scores."""
        weights = {
            "metadata": 0.25,
            "litigation_hops": 0.30,
            "pleadings": 0.15,
            "decisions": 0.20,
            "documents": 0.10
        }

        weighted_score = 0.0
        total_weight = 0.0

        for component, score in component_scores.items():
            weight = weights.get(component, 0.0)
            weighted_score += score * weight
            total_weight += weight

        return weighted_score / total_weight if total_weight > 0 else 0.0

    def _generate_extraction_notes(self, metadata_quality: Dict[str, Any],
                                 litigation_analysis: Dict[str, Any],
                                 content_analysis: Dict[str, Any],
                                 document_analysis: Dict[str, Any]) -> List[str]:
        """Generate extraction notes from analysis results."""
        notes = []

        # Add metadata notes
        if metadata_quality["issues"]:
            notes.extend([f"Metadata: {issue}" for issue in metadata_quality["issues"]])
        if metadata_quality["strengths"]:
            notes.extend([f"Metadata: {strength}" for strength in metadata_quality["strengths"]])

        # Add litigation notes
        if litigation_analysis["issues"]:
            notes.extend([f"Litigation: {issue}" for issue in litigation_analysis["issues"]])
        if litigation_analysis["strengths"]:
            notes.extend([f"Litigation: {strength}" for strength in litigation_analysis["strengths"]])

        # Add content notes
        if content_analysis["issues"]:
            notes.extend([f"Content: {issue}" for issue in content_analysis["issues"]])
        if content_analysis["strengths"]:
            notes.extend([f"Content: {strength}" for strength in content_analysis["strengths"]])

        # Add document notes
        if document_analysis["issues"]:
            notes.extend([f"Documents: {issue}" for issue in document_analysis["issues"]])
        if document_analysis["strengths"]:
            notes.extend([f"Documents: {strength}" for strength in document_analysis["strengths"]])

        return notes

    async def analyze_multiple_cases(self, cases: List[Case]) -> List[AnalysisResult]:
        """
        Analyze multiple cases concurrently.

        Args:
            cases: List of cases to analyze

        Returns:
            List of analysis results
        """
        logger.info(f"Analyzing {len(cases)} cases")

        tasks = [self.analyze_case(case) for case in cases]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failed analyses
        successful_results = []
        for result in results:
            if isinstance(result, AnalysisResult):
                successful_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Case analysis failed: {str(result)}")

        logger.info(f"Successfully analyzed {len(successful_results)} out of {len(cases)} cases")
        return successful_results