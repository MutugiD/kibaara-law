# Local Testing Guide for Legal Assistant Backend

## Overview
This document provides step-by-step instructions for testing the legal assistant backend locally, including all components and the complete end-to-end workflow.

## Prerequisites

### Environment Setup
```bash
# Activate virtual environment
source law_env/bin/activate

# Verify Python version
python --version  # Should be 3.12.x

# Check installed packages
pip list | grep -E "(openai|aiohttp|beautifulsoup4|PyPDF2|loguru)"
```

### API Keys Configuration
Ensure `.env` file contains:
```env
OPENAI_API_KEY=your_openai_api_key_here
SERP_API_KEY=your_serp_api_key_here
```

## Testing Procedures

### 1. Basic Service Initialization Test

**File**: `test_service_initialization.py`
**Purpose**: Verify all services can be initialized without errors

```bash
python test_service_initialization.py
```

**Expected Output**:
- All services initialized successfully
- No import errors
- Cache service working
- PDF processor modules loaded

### 2. Cache Service Test

**File**: `test_cache_service.py`
**Purpose**: Test caching functionality for avoiding re-processing

```bash
python test_cache_service.py
```

**Expected Output**:
- Cache service initialized
- Test data cached successfully
- Cache retrieval working
- Cache statistics updated

### 3. PDF Downloader Test

**File**: `test_pdf_downloader.py`
**Purpose**: Test PDF downloading with cache support

```bash
python test_pdf_downloader.py
```

**Expected Output**:
- PDFs downloaded to `data/raw/`
- Cache entries created
- Duplicate downloads avoided
- Error handling for failed downloads

### 4. PDF Analysis Test

**File**: `test_pdf_analysis.py`
**Purpose**: Test PDF text extraction and analysis

```bash
python test_pdf_analysis.py
```

**Expected Output**:
- PDF text extracted successfully
- Processed content saved to `data/processed/`
- Analysis results cached
- Pleadings and rulings identified

### 5. End-to-End Workflow Test

**File**: `law_data_processor.py`
**Purpose**: Test complete workflow from prompt to final results

```bash
python law_data_processor.py
```

**Expected Output**:
- Prompt processing completed
- Serp search successful (10+ results)
- LLM analysis completed (5+ cases)
- PDF downloads successful (8 PDFs)
- Case analysis completed
- Final results saved to `results/final_analysis_results.json`

## Current Testing Results

### ✅ Working Components

1. **Service Initialization**
   - All services initialize without errors
   - Dependencies resolved correctly
   - Cache service functional

2. **Prompt Processing**
   - PromptProcessor handles user queries
   - Search criteria extracted correctly
   - Prompt objects created successfully

3. **Serp Search**
   - Live web search working
   - 37 raw results found
   - 10 filtered results returned
   - Real Kenyan court cases identified

4. **LLM Analysis**
   - GPT-4o integration working
   - 5 cases with 2-hop litigation identified
   - Case information extracted correctly
   - Analysis results parsed successfully

5. **PDF Downloading**
   - 8 PDF files downloaded successfully
   - Cache prevents re-downloading
   - Error handling for 403 responses
   - Files saved to `data/raw/`

6. **PDF Processing**
   - Text extraction working
   - Content cleaned and normalized
   - Sections extracted correctly
   - Processed files saved to `data/processed/`

7. **Case Analysis**
   - Litigation hops detected
   - Legal principles identified
   - Case metadata extracted
   - Analysis results cached

### ⚠️ Known Issues

1. **Filtering Logic**
   - Appellate court detection needs improvement
   - Some cases not being filtered correctly
   - Need to handle different court name formats

2. **PDF Analysis Performance**
   - Large PDFs take time to process
   - Memory usage could be optimized
   - Need better error handling for corrupted PDFs

3. **Error Handling**
   - Some edge cases not handled
   - Network timeouts could be improved
   - Better logging for debugging

## Test Data Generated

### Files Created
- **PDFs**: 8 files in `data/raw/`
- **Processed**: 1 file in `data/processed/`
- **Cache**: 2 files in `cache/`
- **Results**: 5 files in `results/`

### Sample Results
```json
{
  "workflow_summary": {
    "total_cases_found": 5,
    "cases_with_2hop_litigation": 5,
    "cases_ending_in_appellate": 1,
    "pdfs_downloaded": 8,
    "cases_analyzed": 1,
    "pdfs_analyzed": 1
  }
}
```

## Debugging Procedures

### 1. Check Logs
```bash
# View recent logs
tail -f logs/legal_assistant.log

# Search for errors
grep ERROR logs/legal_assistant.log
```

### 2. Verify Cache
```bash
# Check cache contents
cat cache/test_cache.json | jq .

# Clear cache if needed
rm cache/*.json
```

### 3. Test Individual Components
```bash
# Test specific service
python -c "from src.services.llm_service import LLMService; print('LLMService OK')"

# Test PDF processing
python -c "from src.pdf_processor.pdf_extractor import PDFExtractor; print('PDFExtractor OK')"
```

### 4. Check API Keys
```bash
# Verify environment variables
python -c "import os; print('OpenAI:', bool(os.getenv('OPENAI_API_KEY'))); print('Serp:', bool(os.getenv('SERP_API_KEY')))"
```

## Performance Metrics

### Current Performance
- **Serp Search**: ~10 seconds for 10 results
- **LLM Analysis**: ~30 seconds for 5 cases
- **PDF Download**: ~20 seconds for 8 PDFs
- **PDF Processing**: ~5 seconds per PDF
- **Total Workflow**: ~2-3 minutes

### Optimization Opportunities
- Parallel PDF processing
- Batch LLM requests
- Improved caching strategies
- Memory usage optimization

## Next Testing Steps

1. **Unit Tests**: Add comprehensive unit tests for all services
2. **Integration Tests**: Test service interactions
3. **Performance Tests**: Benchmark with larger datasets
4. **Error Recovery Tests**: Test system recovery from failures
5. **Load Tests**: Test with multiple concurrent requests

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure virtual environment is activated
   - Check all dependencies are installed
   - Verify Python path includes src directory

2. **API Key Errors**
   - Verify .env file exists and has correct keys
   - Check API key validity
   - Ensure proper environment variable loading

3. **PDF Download Failures**
   - Check network connectivity
   - Verify URL accessibility
   - Review error logs for specific issues

4. **Memory Issues**
   - Monitor system resources
   - Consider processing PDFs in smaller batches
   - Implement memory cleanup

### Support Commands
```bash
# Full system check
python -c "
import sys
print('Python:', sys.version)
import openai; print('OpenAI: OK')
import aiohttp; print('aiohttp: OK')
import bs4; print('beautifulsoup4: OK')
import PyPDF2; print('PyPDF2: OK')
from loguru import logger; print('loguru: OK')
print('All dependencies: OK')
"
```

## Frontend Implementation Testing

### ✅ Completed Tests

#### 1. Frontend Setup
- **Test**: React+TypeScript project creation
- **Status**: ✅ PASSED
- **Details**: Project created successfully with all dependencies installed

#### 2. Material-UI Integration
- **Test**: Material-UI components and Grid2 implementation
- **Status**: ✅ PASSED
- **Details**: All components render correctly, Grid2 TypeScript errors fixed

#### 3. Redux Store Configuration
- **Test**: Redux Toolkit setup with search slice
- **Status**: ✅ PASSED
- **Details**: Store configured with proper middleware and async thunks

#### 4. API Service
- **Test**: Axios configuration and API endpoints
- **Status**: ✅ PASSED
- **Details**: API service configured with interceptors and error handling

#### 5. Component Implementation
- **Test**: Search form, results, and page components
- **Status**: ✅ PASSED
- **Details**: All components implemented with proper TypeScript types

### ✅ Backend Integration Tests

#### 1. FastAPI Server
- **Test**: Server startup and health check
- **Status**: ✅ PASSED
- **Command**: `uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload`
- **Result**: Server running on port 8000

#### 2. Health Endpoint
- **Test**: `/health` endpoint response
- **Status**: ✅ PASSED
- **Response**: `{"status":"healthy","service":"legal-assistant-api","version":"1.0.0"}`

#### 3. Search Endpoint
- **Test**: `/api/v1/cases/search` endpoint
- **Status**: ✅ PASSED
- **Query**: `contract&max_results=3`
- **Response**: JSON with 3 case results

### ✅ Data Pipeline Tests

#### 1. Legal Data Processor
- **Test**: End-to-end pipeline execution
- **Status**: ✅ PASSED
- **Command**: `python law_data_processor.py --query "contract dispute" --max_results 3 --download_pdfs`
- **Results**:
  - Serp search: 10 results found
  - LLM analysis: 5 cases analyzed
  - 2-hop filtering: 5 cases passed
  - PDF downloads: 1/2 cases successful
  - Case analysis: 2/2 successful
  - PDF analysis: 4/4 successful

#### 2. File Generation
- **Test**: Output files creation
- **Status**: ✅ PASSED
- **Files Created**:
  - `results/final_analysis_results.json` (506KB)
  - `results/parsed_llm_analysis.json`
  - `results/two_hop_filtering_results.json`
  - Analysis results in subdirectories

### 🔄 Current Testing Status

#### Frontend Services
- **React Development Server**: ✅ Running on port 3000
- **FastAPI Backend**: ✅ Running on port 8000
- **API Communication**: ✅ Endpoints responding correctly

#### Integration Points
- **Frontend-Backend**: ⚠️ Needs browser testing
- **External IP Access**: ❌ Not accessible (172.190.55.213:8000)
- **Local Development**: ✅ Working correctly

## Testing Commands

### Start Services
```bash
# Start FastAPI backend
cd /home/azureuser/kibaara-law
source law_env/bin/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Start React frontend (in new terminal)
cd frontend
npm start
```

### Test API Endpoints
```bash
# Health check
curl -X GET "http://localhost:8000/health" -H "accept: application/json"

# Search cases
curl -X GET "http://localhost:8000/api/v1/cases/search?query=contract&max_results=3" -H "accept: application/json"

# Raw cases
curl -X GET "http://localhost:8000/api/v1/cases/raw?limit=5" -H "accept: application/json"
```

### Test Data Pipeline
```bash
# Run complete pipeline
python law_data_processor.py --query "contract dispute" --max_results 3 --download_pdfs

# Check results
ls -la results/
cat results/final_analysis_results.json | jq '.summary'
```

## Known Issues

### 1. External IP Access
- **Issue**: FastAPI server not accessible via external IP (172.190.55.213:8000)
- **Status**: Under investigation
- **Workaround**: Use localhost for development

### 2. PDF Download Success Rate
- **Issue**: Only 1/2 cases had PDFs available for download
- **Status**: Expected behavior (not all cases have PDFs)
- **Impact**: Minimal - analysis still works with available data

## Next Testing Steps

1. **Browser Integration Test**
   - Open http://localhost:3000 in browser
   - Test search functionality
   - Verify results display correctly

2. **Error Handling Test**
   - Test with invalid queries
   - Test network failures
   - Verify error messages display correctly

3. **Responsive Design Test**
   - Test on different screen sizes
   - Verify mobile responsiveness

4. **Performance Test**
   - Test with large result sets
   - Monitor loading times
   - Check memory usage

## Backend Refactor and Pipeline Test

- Renamed src/ to backend/
- Updated all import paths in backend and root scripts
- Fixed all service initializations to use config values (api keys, etc.)
- Removed invalid async/await usage for sync methods
- Fixed class name mismatches (PDFDownloader, get_config, etc.)
- Ran law_data_processor.py with test query
- Pipeline completed successfully, logs show all steps executed
- No errors in final run, results saved to results/final_analysis_results.json

## Next Steps
- Review frontend API calls for compatibility with new backend structure
- Add more robust error handling and logging for new backend
- Implement user upload endpoint
- Add more comprehensive integration tests