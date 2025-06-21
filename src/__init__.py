"""
Legal Assistant Backend - Main Package

This package provides a comprehensive legal assistant backend for finding and analyzing
Kenyan court cases with multi-hop litigation processes.
"""

# Core services
from .services.prompt_processor import PromptProcessor
from .services.serp_search_service import SerpSearchService
from .services.llm_service import LLMService
from .services.pdf_downloader import PDFDownloader
from .services.case_analyzer import CaseAnalyzer
from .services.result_formatter import ResultFormatter
from .services.cache_service import CacheService
from .services.pdf_analysis_service import PDFAnalysisService

# Prompt services
from .prompt_services.pleadings_prompts import PleadingsPrompts
from .prompt_services.rulings_prompts import RulingsPrompts
from .prompt_services.summary_prompts import SummaryPrompts

# PDF processing
from .pdf_processor.pdf_extractor import PDFExtractor
from .pdf_processor.pdf_analyzer import PDFAnalyzer

# Models
from .models.case_models import Case, CaseMetadata, LitigationHop, CourtLevel, CaseStatus
from .models.prompt_models import LegalPrompt, SearchCriteria, Prompt, AnalysisRequest

# Utils
from .utils.config import Config

__version__ = "1.0.0"
__author__ = "Legal Assistant Team"

# Export main classes for easy access
__all__ = [
    # Core services
    "PromptProcessor",
    "SerpSearchService",
    "LLMService",
    "PDFDownloader",
    "CaseAnalyzer",
    "ResultFormatter",
    "CacheService",
    "PDFAnalysisService",

    # Prompt services
    "PleadingsPrompts",
    "RulingsPrompts",
    "SummaryPrompts",

    # PDF processing
    "PDFExtractor",
    "PDFAnalyzer",

    # Models
    "Case",
    "CaseMetadata",
    "LitigationHop",
    "CourtLevel",
    "CaseStatus",
    "LegalPrompt",
    "SearchCriteria",
    "Prompt",
    "AnalysisRequest",

    # Utils
    "Config"
]