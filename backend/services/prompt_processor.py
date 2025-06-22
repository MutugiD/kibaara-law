"""
Prompt processing service for legal research requests.

This module handles the parsing and analysis of user prompts to extract
search criteria and requirements for legal case research.
"""

import re
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from loguru import logger

from ..models.prompt_models import Prompt, SearchCriteria, AnalysisRequest
from ..models.case_models import CourtLevel


class PromptProcessor:
    """
    Service for processing and analyzing user prompts.

    This service extracts structured search criteria from natural language
    prompts and validates the requirements for legal research.
    """

    def __init__(self) -> None:
        """Initialize the prompt processor."""
        self.court_level_patterns = {
            CourtLevel.MAGISTRATE: r'\b(magistrate|magistrate\'s court|lower court)\b',
            CourtLevel.HIGH_COURT: r'\b(high court|superior court)\b',
            CourtLevel.COURT_OF_APPEAL: r'\b(court of appeal|appellate court|appeal)\b',
            CourtLevel.SUPREME_COURT: r'\b(supreme court|highest court)\b'
        }

        self.number_patterns = [
            r'(\d+)\s*(?:distinct|different|unique|separate)\s*cases?',
            r'find\s*(\d+)\s*cases?',
            r'(\d+)\s*cases?\s*that',
            r'(\d+)\s*court\s*cases?'
        ]

        self.hop_patterns = [
            r'two-hop\s*litigation',
            r'multi-hop\s*litigation',
            r'(\d+)\s*hop\s*litigation',
            r'litigation\s*process.*(\d+)\s*hop',
            r'starting.*trial.*proceeding.*appellate'
        ]

    def process_prompt(self, prompt_text: str, user_id: Optional[str] = None) -> Prompt:
        """
        Process a user prompt and extract search criteria.

        Args:
            prompt_text: The natural language prompt from the user
            user_id: Optional user identifier

        Returns:
            Prompt object with extracted search criteria

        Raises:
            ValueError: If prompt cannot be processed or is invalid
        """
        logger.info(f"Processing prompt: {prompt_text[:100]}...")

        try:
            # Extract search criteria
            search_criteria = self._extract_search_criteria(prompt_text)

            # Create prompt object
            prompt = Prompt(
                text=prompt_text,
                search_criteria=search_criteria,
                user_id=user_id,
                timestamp=datetime.now()
            )

            logger.info(f"Successfully processed prompt with {search_criteria.case_count} cases requested")
            return prompt

        except Exception as e:
            logger.error(f"Failed to process prompt: {str(e)}")
            raise ValueError(f"Failed to process prompt: {str(e)}")

    def _extract_search_criteria(self, prompt_text: str) -> SearchCriteria:
        """
        Extract structured search criteria from prompt text.

        Args:
            prompt_text: The natural language prompt

        Returns:
            SearchCriteria object with extracted parameters
        """
        # Extract case count
        case_count = self._extract_case_count(prompt_text)

        # Extract court levels
        court_levels = self._extract_court_levels(prompt_text)

        # Extract date range
        date_from, date_to = self._extract_date_range(prompt_text)

        # Extract subject matter
        subject_matter = self._extract_subject_matter(prompt_text)

        # Extract case type
        case_type = self._extract_case_type(prompt_text)

        # Extract parties
        parties = self._extract_parties(prompt_text)

        # Extract keywords
        keywords = self._extract_keywords(prompt_text)

        # Determine multi-hop requirements
        require_multi_hop, min_hops = self._extract_multi_hop_requirements(prompt_text)

        return SearchCriteria(
            case_count=case_count,
            court_levels=court_levels,
            date_from=date_from,
            date_to=date_to,
            subject_matter=subject_matter,
            case_type=case_type,
            parties=parties,
            keywords=keywords,
            require_multi_hop=require_multi_hop,
            min_hops=min_hops
        )

    def _extract_case_count(self, text: str) -> int:
        """Extract the number of cases requested."""
        text_lower = text.lower()

        for pattern in self.number_patterns:
            match = re.search(pattern, text_lower)
            if match:
                count = int(match.group(1))
                return min(count, 100)  # Cap at 100 cases

        # Default to 5 if not specified
        return 5

    def _extract_court_levels(self, text: str) -> List[CourtLevel]:
        """Extract court levels mentioned in the prompt."""
        text_lower = text.lower()
        court_levels = []

        for court_level, pattern in self.court_level_patterns.items():
            if re.search(pattern, text_lower):
                court_levels.append(court_level)

        return court_levels

    def _extract_date_range(self, text: str) -> tuple[Optional[date], Optional[date]]:
        """Extract date range from the prompt."""
        # Simple date extraction - can be enhanced
        # For now, return None for both dates
        return None, None

    def _extract_subject_matter(self, text: str) -> Optional[str]:
        """Extract subject matter from the prompt."""
        # Look for common legal subject matters
        subject_patterns = [
            r'focus\s+on\s+(.+?)(?:\s+with|\s+that|\s+and)',
            r'cases?\s+(?:about|regarding|concerning)\s+(.+?)(?:\s+with|\s+that|\s+and)',
            r'subject\s+matter.*?(\w+(?:\s+\w+)*)'
        ]

        for pattern in subject_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_case_type(self, text: str) -> Optional[str]:
        """Extract case type from the prompt."""
        text_lower = text.lower()

        case_types = {
            'civil': r'\bcivil\b',
            'criminal': r'\bcriminal\b',
            'constitutional': r'\bconstitutional\b',
            'commercial': r'\bcommercial\b',
            'family': r'\bfamily\b',
            'land': r'\bland\b',
            'employment': r'\bemployment\b'
        }

        for case_type, pattern in case_types.items():
            if re.search(pattern, text_lower):
                return case_type

        return None

    def _extract_parties(self, text: str) -> List[str]:
        """Extract party names from the prompt."""
        # Simple party extraction - can be enhanced with NLP
        parties = []

        # Look for patterns like "between X and Y" or "X v Y"
        party_patterns = [
            r'between\s+([^,]+?)\s+and\s+([^,]+?)(?:\s+with|\s+that|\s+and)',
            r'(\w+(?:\s+\w+)*)\s+v\s+(\w+(?:\s+\w+)*)',
            r'parties?\s+(.+?)(?:\s+with|\s+that|\s+and)'
        ]

        for pattern in party_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    parties.extend([p.strip() for p in match])
                else:
                    parties.append(match.strip())

        return list(set(parties))  # Remove duplicates

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract additional keywords from the prompt."""
        # Remove common words and extract meaningful keywords
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'find', 'search', 'case', 'cases', 'court', 'courts', 'litigation',
            'process', 'trial', 'appellate', 'appeal', 'decision', 'ruling'
        }

        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]

        return list(set(keywords))  # Remove duplicates

    def _extract_multi_hop_requirements(self, text: str) -> tuple[bool, int]:
        """Extract multi-hop litigation requirements."""
        text_lower = text.lower()

        # Check for multi-hop patterns
        for pattern in self.hop_patterns:
            match = re.search(pattern, text_lower)
            if match:
                if 'two-hop' in pattern or '2-hop' in pattern:
                    return True, 2
                elif match.groups():
                    return True, int(match.group(1))
                else:
                    return True, 2

        # Check for specific hop counts
        hop_count_match = re.search(r'(\d+)\s*hop', text_lower)
        if hop_count_match:
            return True, int(hop_count_match.group(1))

        # Default to requiring multi-hop with minimum 2 hops
        return True, 2

    def validate_prompt(self, prompt: Prompt) -> List[str]:
        """
        Validate a processed prompt and return any issues.

        Args:
            prompt: The processed prompt to validate

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        # Check if search criteria are reasonable
        if prompt.search_criteria.case_count > 50:
            issues.append("Requested case count is very high (>50)")

        if not prompt.search_criteria.court_levels:
            issues.append("No specific court levels identified")

        if prompt.search_criteria.min_hops > 4:
            issues.append("Minimum hops requirement is very high (>4)")

        # Check for ambiguous requirements
        if len(prompt.search_criteria.keywords) < 2:
            issues.append("Very few keywords extracted - search may be too broad")

        return issues

    def create_analysis_request(self, prompt: Prompt, case_urls: List[str]) -> AnalysisRequest:
        """
        Create an analysis request from a processed prompt.

        Args:
            prompt: The processed prompt
            case_urls: List of case URLs to analyze

        Returns:
            AnalysisRequest object
        """
        return AnalysisRequest(
            prompt=prompt,
            case_urls=case_urls,
            analysis_type="full",
            include_documents=True,
            include_related_cases=True,
            output_format="json"
        )