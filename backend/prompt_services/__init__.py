"""
Prompt Services Package

This package contains specialized prompt services for legal document analysis.
"""

from .pleadings_prompts import PleadingsPrompts
from .rulings_prompts import RulingsPrompts
from .summary_prompts import SummaryPrompts

__all__ = [
    "PleadingsPrompts",
    "RulingsPrompts",
    "SummaryPrompts"
]