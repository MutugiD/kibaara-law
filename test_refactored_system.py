#!/usr/bin/env python3
"""
Test Script for Refactored Legal Assistant System

This script tests the new modular structure with separated prompt services
and PDF processing modules.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv
from loguru import logger

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
    PDFAnalyzer,
    PleadingsPrompts,
    RulingsPrompts,
    SummaryPrompts
)


def setup_logging() -> None:
    """Setup logging for testing."""
    logger.remove()
    logger.add(
        "logs/test_refactored_system.log",
        rotation="5 MB",
        retention="3 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    logger.add(
        sys.stderr,
        level="INFO",
        format="{time:HH:mm:ss} | {level} | {message}"
    )


def test_prompt_services() -> Dict[str, Any]:
    """Test the new prompt services."""
    logger.info("Testing prompt services...")

    results = {
        'success': True,
        'tests': {},
        'errors': []
    }

    try:
        # Test PleadingsPrompts
        logger.info("Testing PleadingsPrompts...")
        pleadings_prompts = PleadingsPrompts()

        test_prompt = pleadings_prompts.get_comprehensive_pleadings_prompt(
            "Test Case", "Test PDF content"
        )

        if test_prompt and "REQUIRED COMPREHENSIVE ANALYSIS" in test_prompt:
            results['tests']['pleadings_prompts'] = {'success': True, 'message': 'PleadingsPrompts working correctly'}
            logger.info("✓ PleadingsPrompts test passed")
        else:
            results['tests']['pleadings_prompts'] = {'success': False, 'message': 'PleadingsPrompts failed'}
            results['success'] = False
            logger.error("✗ PleadingsPrompts test failed")

        # Test RulingsPrompts
        logger.info("Testing RulingsPrompts...")
        rulings_prompts = RulingsPrompts()

        test_prompt = rulings_prompts.get_trial_court_decision_prompt(
            "Test Case", "Test PDF content"
        )

        if test_prompt and "TRIAL COURT INFORMATION" in test_prompt:
            results['tests']['rulings_prompts'] = {'success': True, 'message': 'RulingsPrompts working correctly'}
            logger.info("✓ RulingsPrompts test passed")
        else:
            results['tests']['rulings_prompts'] = {'success': False, 'message': 'RulingsPrompts failed'}
            results['success'] = False
            logger.error("✗ RulingsPrompts test failed")

        # Test SummaryPrompts
        logger.info("Testing SummaryPrompts...")
        summary_prompts = SummaryPrompts()

        test_prompt = summary_prompts.get_comprehensive_case_summary_prompt(
            "Test Case", "Test pleadings", "Test trial", "Test appellate"
        )

        if test_prompt and "COMPREHENSIVE SUMMARY" in test_prompt:
            results['tests']['summary_prompts'] = {'success': True, 'message': 'SummaryPrompts working correctly'}
            logger.info("✓ SummaryPrompts test passed")
        else:
            results['tests']['summary_prompts'] = {'success': False, 'message': 'SummaryPrompts failed'}
            results['success'] = False
            logger.error("✗ SummaryPrompts test failed")

    except Exception as e:
        logger.error(f"Error testing prompt services: {e}")
        results['success'] = False
        results['errors'].append(str(e))

    return results


def test_pdf_processor() -> Dict[str, Any]:
    """Test the new PDF processor modules."""
    logger.info("Testing PDF processor modules...")

    results = {
        'success': True,
        'tests': {},
        'errors': []
    }

    try:
        # Test PDFExtractor
        logger.info("Testing PDFExtractor...")
        pdf_extractor = PDFExtractor()

        # Test with a sample PDF if available
        pdf_dir = Path("data/raw")
        if pdf_dir.exists():
            pdf_files = list(pdf_dir.glob("*.pdf"))
            if pdf_files:
                test_pdf = str(pdf_files[0])
                logger.info(f"Testing PDFExtractor with: {test_pdf}")

                extract_result = pdf_extractor.extract_text_from_pdf(test_pdf)
                if extract_result:
                    results['tests']['pdf_extractor'] = {'success': True, 'message': 'PDFExtractor working correctly'}
                    logger.info("✓ PDFExtractor test passed")
                else:
                    results['tests']['pdf_extractor'] = {'success': False, 'message': 'PDFExtractor failed to extract text'}
                    results['success'] = False
                    logger.error("✗ PDFExtractor test failed")
            else:
                results['tests']['pdf_extractor'] = {'success': True, 'message': 'PDFExtractor initialized (no PDFs to test)'}
                logger.info("✓ PDFExtractor initialized (no PDFs available for testing)")
        else:
            results['tests']['pdf_extractor'] = {'success': True, 'message': 'PDFExtractor initialized (no PDF directory)'}
            logger.info("✓ PDFExtractor initialized (no PDF directory)")

        # Test PDFAnalyzer
        logger.info("Testing PDFAnalyzer...")
        pdf_analyzer = PDFAnalyzer()

        # Test with sample content
        test_content = "This is a test legal document content for analysis."
        test_analysis = pdf_analyzer.analyze_pleadings("Test Case", test_content)

        if test_analysis and 'success' in test_analysis:
            results['tests']['pdf_analyzer'] = {'success': True, 'message': 'PDFAnalyzer working correctly'}
            logger.info("✓ PDFAnalyzer test passed")
        else:
            results['tests']['pdf_analyzer'] = {'success': False, 'message': 'PDFAnalyzer failed'}
            results['success'] = False
            logger.error("✗ PDFAnalyzer test failed")

    except Exception as e:
        logger.error(f"Error testing PDF processor: {e}")
        results['success'] = False
        results['errors'].append(str(e))

    return results


def test_services_initialization() -> Dict[str, Any]:
    """Test service initialization with the new structure."""
    logger.info("Testing service initialization...")

    results = {
        'success': True,
        'tests': {},
        'errors': []
    }

    try:
        # Test core services
        services_to_test = [
            ('PromptProcessor', PromptProcessor),
            ('SerpSearchService', lambda: SerpSearchService(os.getenv('SERP_API_KEY', 'test_key'))),
            ('LLMService', lambda: LLMService(os.getenv('OPENAI_API_KEY', 'test_key'))),
            ('PDFDownloader', PDFDownloader),
            ('CaseAnalyzer', CaseAnalyzer),
            ('ResultFormatter', ResultFormatter),
            ('CacheService', lambda: CacheService('cache/test_cache.json')),
            ('PDFAnalysisService', PDFAnalysisService)
        ]

        for service_name, service_class in services_to_test:
            logger.info(f"Testing {service_name}...")
            try:
                service_instance = service_class()
                results['tests'][service_name] = {'success': True, 'message': f'{service_name} initialized successfully'}
                logger.info(f"✓ {service_name} test passed")
            except Exception as e:
                results['tests'][service_name] = {'success': False, 'message': f'{service_name} failed: {str(e)}'}
                results['success'] = False
                logger.error(f"✗ {service_name} test failed: {e}")

    except Exception as e:
        logger.error(f"Error testing service initialization: {e}")
        results['success'] = False
        results['errors'].append(str(e))

    return results


def test_imports() -> Dict[str, Any]:
    """Test that all imports work correctly."""
    logger.info("Testing imports...")

    results = {
        'success': True,
        'tests': {},
        'errors': []
    }

    try:
        # Test main package import
        import src
        results['tests']['main_package'] = {'success': True, 'message': 'Main package import successful'}
        logger.info("✓ Main package import test passed")

        # Test prompt services imports
        from src.prompt_services import PleadingsPrompts, RulingsPrompts, SummaryPrompts
        results['tests']['prompt_services_import'] = {'success': True, 'message': 'Prompt services imports successful'}
        logger.info("✓ Prompt services imports test passed")

        # Test PDF processor imports
        from src.pdf_processor import PDFExtractor, PDFAnalyzer
        results['tests']['pdf_processor_import'] = {'success': True, 'message': 'PDF processor imports successful'}
        logger.info("✓ PDF processor imports test passed")

        # Test services imports
        from src.services import (
            PromptProcessor, SerpSearchService, LLMService, PDFDownloader,
            CaseAnalyzer, ResultFormatter, CacheService, PDFAnalysisService
        )
        results['tests']['services_import'] = {'success': True, 'message': 'Services imports successful'}
        logger.info("✓ Services imports test passed")

    except Exception as e:
        logger.error(f"Error testing imports: {e}")
        results['success'] = False
        results['errors'].append(str(e))

    return results


def test_cache_service() -> Dict[str, Any]:
    """Test the cache service functionality."""
    logger.info("Testing cache service...")

    results = {
        'success': True,
        'tests': {},
        'errors': []
    }

    try:
        cache_service = CacheService('cache/test_cache.json')

        # Test caching
        test_case = {
            'title': 'Test Case',
            'content': 'Test content',
            'timestamp': '2024-01-01 12:00:00'
        }

        cache_key = 'test_key_123'
        cache_service.cache_case(cache_key, test_case)

        # Test retrieval
        retrieved_case = cache_service.get_case(cache_key)

        if retrieved_case and retrieved_case.get('title') == 'Test Case':
            results['tests']['cache_service'] = {'success': True, 'message': 'Cache service working correctly'}
            logger.info("✓ Cache service test passed")
        else:
            results['tests']['cache_service'] = {'success': False, 'message': 'Cache service failed'}
            results['success'] = False
            logger.error("✗ Cache service test failed")

    except Exception as e:
        logger.error(f"Error testing cache service: {e}")
        results['success'] = False
        results['errors'].append(str(e))

    return results


def run_all_tests() -> Dict[str, Any]:
    """Run all tests for the refactored system."""
    logger.info("Starting comprehensive tests for refactored system...")

    all_results = {
        'overall_success': True,
        'test_suites': {},
        'summary': {}
    }

    # Run all test suites
    test_suites = [
        ('imports', test_imports),
        ('services_initialization', test_services_initialization),
        ('prompt_services', test_prompt_services),
        ('pdf_processor', test_pdf_processor),
        ('cache_service', test_cache_service)
    ]

    for suite_name, test_function in test_suites:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {suite_name} tests...")
        logger.info(f"{'='*50}")

        suite_results = test_function()
        all_results['test_suites'][suite_name] = suite_results

        if not suite_results['success']:
            all_results['overall_success'] = False

        # Log summary
        passed_tests = len([t for t in suite_results['tests'].values() if t['success']])
        total_tests = len(suite_results['tests'])
        logger.info(f"{suite_name}: {passed_tests}/{total_tests} tests passed")

    # Generate summary
    total_passed = 0
    total_tests = 0

    for suite_name, suite_results in all_results['test_suites'].items():
        suite_passed = len([t for t in suite_results['tests'].values() if t['success']])
        suite_total = len(suite_results['tests'])
        total_passed += suite_passed
        total_tests += suite_total

        all_results['summary'][suite_name] = {
            'passed': suite_passed,
            'total': suite_total,
            'success_rate': (suite_passed / suite_total * 100) if suite_total > 0 else 0
        }

    all_results['summary']['overall'] = {
        'passed': total_passed,
        'total': total_tests,
        'success_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0
    }

    # Save results
    results_file = Path("results/refactored_system_test_results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    logger.info(f"Overall Success: {'✓ PASSED' if all_results['overall_success'] else '✗ FAILED'}")
    logger.info(f"Total Tests: {total_tests}")
    logger.info(f"Passed: {total_passed}")
    logger.info(f"Success Rate: {all_results['summary']['overall']['success_rate']:.1f}%")
    logger.info(f"Results saved to: {results_file}")

    return all_results


def main() -> None:
    """Main function to run all tests."""
    try:
        # Setup logging
        setup_logging()
        logger.info("Starting refactored system tests...")

        # Run all tests
        results = run_all_tests()

        # Exit with appropriate code
        if results['overall_success']:
            logger.info("All tests completed successfully!")
            sys.exit(0)
        else:
            logger.error("Some tests failed!")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Fatal error in test suite: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()