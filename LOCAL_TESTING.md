# Local Testing Guide - Legal Assistant

This guide provides step-by-step instructions for testing the legal assistant functionality locally.

## Prerequisites

### System Requirements
- Python 3.11 or higher
- Chrome browser (for web scraping)
- At least 4GB RAM
- Stable internet connection

### Dependencies Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Chrome installation:**
   ```bash
   google-chrome --version
   # or
   chromium-browser --version
   ```

3. **Create necessary directories:**
   ```bash
   mkdir -p logs results
   ```

## Testing Workflow

### 1. Basic Functionality Test

**Command:**
```bash
python law_data_processor.py
```

**Expected Behavior:**
- Script should start and show logging information
- Should attempt to search for cases on Kenya Law
- Should download and analyze cases
- Should generate a summary report

**Success Indicators:**
- No critical errors in logs
- Results file generated in `results/legal_analysis_result.txt`
- Processing time under 5 minutes

### 2. Component Testing

#### Test Prompt Processing
```python
from src.services.prompt_processor import PromptProcessor

processor = PromptProcessor()
prompt_text = "Find 3 Kenyan court cases about land disputes with multi-hop litigation"
prompt = processor.process_prompt(prompt_text)
print(f"Extracted {prompt.search_criteria.case_count} cases")
print(f"Keywords: {prompt.search_criteria.keywords}")
```

#### Test Search Engine
```python
from src.services.search_engine import SearchEngine
import asyncio

async def test_search():
    engine = SearchEngine()
    # Test with mock criteria
    criteria = {"keywords": ["land", "dispute"], "case_count": 2}
    results = await engine.scraper.search_cases(criteria)
    print(f"Found {len(results)} results")
    await engine.close()

asyncio.run(test_search())
```

#### Test Case Analyzer
```python
from src.services.case_analyzer import CaseAnalyzer
from src.models.case_models import Case, CaseMetadata

# Create a test case
metadata = CaseMetadata(case_title="Test Case v Test Respondent")
test_case = Case(metadata=metadata)

analyzer = CaseAnalyzer()
result = await analyzer.analyze_case(test_case)
print(f"Confidence score: {result.confidence_score}")
```

### 3. Error Handling Tests

#### Test Network Issues
```bash
# Disconnect internet and run
python law_data_processor.py
# Should handle gracefully with error message
```

#### Test Invalid Prompts
```python
# Test with empty prompt
prompt = processor.process_prompt("")
# Should raise ValueError

# Test with very long prompt
long_prompt = "test " * 1000
prompt = processor.process_prompt(long_prompt)
# Should raise ValueError for length
```

### 4. Performance Testing

#### Test Large Queries
```python
# Test with larger case count
prompt_text = "Find 20 Kenyan court cases about constitutional matters"
# Should complete within reasonable time (under 10 minutes)
```

#### Test Concurrent Processing
```python
import asyncio
from law_data_processor import LegalDataProcessor

async def test_concurrent():
    processor = LegalDataProcessor()
    prompts = [
        "Find 3 cases about land disputes",
        "Find 3 cases about employment law",
        "Find 3 cases about constitutional rights"
    ]

    tasks = [processor.process_prompt(p) for p in prompts]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results):
        print(f"Prompt {i+1}: {'Success' if not isinstance(result, Exception) else 'Failed'}")

    await processor.close()

asyncio.run(test_concurrent())
```

## Troubleshooting

### Common Issues

#### 1. Chrome WebDriver Issues
**Problem:** `WebDriverException: Message: unknown error: cannot find Chrome binary`

**Solution:**
```bash
# Install Chrome if not present
sudo apt-get update
sudo apt-get install google-chrome-stable

# Or specify Chrome path in code
chrome_options.binary_location = "/usr/bin/google-chrome"
```

#### 2. Import Errors
**Problem:** `ModuleNotFoundError: No module named 'src'`

**Solution:**
```bash
# Add project root to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run from project root
cd /path/to/kibaara-law
python law_data_processor.py
```

#### 3. Permission Errors
**Problem:** `PermissionError: [Errno 13] Permission denied`

**Solution:**
```bash
# Fix file permissions
chmod +x law_data_processor.py
chmod -R 755 src/
chmod -R 755 logs/ results/
```

#### 4. Memory Issues
**Problem:** `MemoryError` or slow performance

**Solution:**
```python
# Reduce concurrent downloads
# In kenya_law_scraper.py, limit concurrent tasks
semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent downloads
```

### Debug Mode

Enable detailed logging for debugging:

```python
# In law_data_processor.py, change log level
logger.add(sys.stderr, level="DEBUG")
```

### Monitoring

#### Check Logs
```bash
# Monitor logs in real-time
tail -f logs/legal_assistant.log

# Search for errors
grep "ERROR" logs/legal_assistant.log

# Search for specific operations
grep "Downloading case" logs/legal_assistant.log
```

#### Check Results
```bash
# View generated results
cat results/legal_analysis_result.txt

# Check file sizes
ls -lh results/
ls -lh logs/
```

## Performance Benchmarks

### Expected Performance Metrics

| Operation | Expected Time | Acceptable Range |
|-----------|---------------|------------------|
| Prompt Processing | < 1 second | 0.1 - 2 seconds |
| Case Search | 5-15 seconds | 3 - 30 seconds |
| Case Download | 10-30 seconds per case | 5 - 60 seconds per case |
| Case Analysis | 2-5 seconds per case | 1 - 10 seconds per case |
| Total Processing | 1-5 minutes | 30 seconds - 10 minutes |

### Resource Usage

| Resource | Expected Usage | Monitoring Command |
|----------|----------------|-------------------|
| CPU | 20-50% during processing | `htop` or `top` |
| Memory | 500MB-2GB | `free -h` |
| Disk | 10-100MB for logs/results | `du -sh logs/ results/` |
| Network | Moderate during downloads | `iftop` or `nethogs` |

## Success Criteria

### Functional Requirements
- [ ] Prompt processing extracts correct criteria
- [ ] Search finds relevant cases
- [ ] Case downloads complete successfully
- [ ] Analysis produces meaningful results
- [ ] Results are properly formatted

### Performance Requirements
- [ ] Processing completes within 5 minutes
- [ ] No memory leaks during operation
- [ ] Error handling works correctly
- [ ] Logs provide useful debugging information

### Quality Requirements
- [ ] Confidence scores are reasonable (0.5-1.0)
- [ ] Multi-hop cases are correctly identified
- [ ] Case metadata is extracted accurately
- [ ] Results are consistent across runs

## Next Steps After Testing

1. **If tests pass:** Proceed to production deployment
2. **If issues found:** Fix bugs and retest
3. **If performance poor:** Optimize code and retest
4. **If functionality incomplete:** Add missing features

## Support

For issues not covered in this guide:
1. Check the logs for detailed error messages
2. Review the code comments for implementation details
3. Test individual components in isolation
4. Consider the Kenya Law website structure may have changed

## Last Test Run: 2025-06-20

### Workflow Steps Validated
- [x] Prompt processing and search query extraction
- [x] Live web search using Serp API (Kenya Law, web, appeal search)
- [x] Filtering and deduplication of search results
- [x] Logging of all search and filtering steps
- [x] LLM (GPT-4o) integration for result analysis (API key error encountered)
- [x] Document downloader service present and ready

### Observations
- Serp search is working and returns real Kenyan court cases.
- LLM step failed due to invalid OpenAI API key (replace with a valid key for full workflow).
- Document download step is ready and will proceed once LLM returns valid cases.

### Next Steps
- Set a valid OpenAI API key in the environment for full LLM analysis.
- Re-run the workflow to validate LLM extraction and document download.
- Add more robust error handling for LLM and document download failures.
- Expand test coverage for edge cases (e.g., no results, partial downloads).