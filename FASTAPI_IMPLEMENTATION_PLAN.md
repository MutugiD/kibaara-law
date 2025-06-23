# FastAPI and Frontend Implementation Plan

## Overview
This document provides a detailed implementation plan for transforming the existing legal assistant backend into a FastAPI service with a React frontend. The plan follows a three-tier architecture approach and leverages existing backend services.

## Architecture Summary

### Three-Tier API Design
1. **Tier 1: Raw Data Layer** - Direct access to legal documents and metadata
2. **Tier 2: Analysis Layer** - Processed legal insights and structured analysis
3. **Tier 3: Application Layer** - User-friendly interfaces and exports

### Technology Stack
- **Backend**: FastAPI with Python 3.12
- **Frontend**: React 18+ with TypeScript
- **UI Library**: Material-UI or Ant Design
- **PDF Viewer**: React-PDF
- **State Management**: Redux Toolkit or Zustand

## Phase 1: Stabilize and Fix Core API (Completed)

- [x] Isolate the FastAPI application from legacy services causing startup crashes.
- [x] Fix cascading `ImportError` issues by disabling unused packages.
- [x] Rename `backend/__init__.py` to break the invalid package structure and prevent erroneous imports.
- [x] Successfully start the server with a minimal, stable application.

## Phase 2: Fix and Enhance Upload Functionality (Completed)

- [x] **Task 1: Diagnose and Fix Upload Endpoint**
  - [x] Investigate and resolve the `400 Bad Request` error.
  - [x] Verify successful file upload via `curl`, ensuring a `200 OK` or `201 Created` response.

- [x] **Task 2: Enhance `Case` Database Model**
  - [x] Add `document_type` field (Enum: `CASE_LAW`, `PLEADINGS`).
  - [x] Add `status` field (Enum: `UPLOADED`, `PROCESSING`, `COMPLETED`, `FAILED`).
  - [x] Ensure `analysis_results` JSON field exists for storing processing output.
  - [x] Apply changes to the database.

- [x] **Task 3: Refactor Upload Endpoint**
  - [x] Modify `POST /api/v1/cases/upload` to accept `document_type` as part of the form data.
  - [x] Update the endpoint logic to save the file and create a `Case` record with the correct `filename`, `status='UPLOADED'`, and `document_type`.

## Phase 3: Implement Processing Workflow (Completed)

- [x] **Task 4: Create Processing Endpoint**
  - [x] Create a new endpoint: `POST /api/v1/cases/{case_id}/process`.
  - [x] This endpoint will change the case `status` from `UPLOADED` to `PROCESSING`.
  - [x] For now, it will contain placeholder logic for the analysis.
  - [x] Upon (mock) completion, it will update the status to `COMPLETED` and add placeholder data to `analysis_results`.

- [x] **Task 5: Refactor "Get All Cases" Endpoint**
  - [x] Modify `GET /api/v1/cases/` to fetch and return all case records from the database.
  - [x] Ensure the response for each case includes all the new fields (`id`, `filename`, `status`, `document_type`, `upload_date`, `analysis_results`).

## Phase 4: Implement Real Analysis (In Progress)

- [ ] **Task 6: Use Filename for Analysis Endpoint**
  - [ ] Modify the `case_service` to fetch a case by `filename` instead of `id`.
  - [ ] Change the processing endpoint from `POST .../{case_id}/process` to `POST .../analyze/{filename}`.
  - [ ] Rename the concept from "processing" to "analysis" in the code.

- [ ] **Task 7: Implement PDF Text Extraction**
  - [ ] Re-enable the `pdf_processor` module.
  - [ ] Integrate a `PDFExtractor` service into the analysis endpoint to extract raw text from the uploaded PDF.
  - [ ] Store the extracted text in the `analysis_results` field in the database.

- [ ] **Task 8: Implement Analysis Download**
  - [ ] Create a new endpoint: `GET /api/v1/cases/download/{filename}`.
  - [ ] This endpoint will fetch the `analysis_results`.
  - [ ] It will return the analysis as a downloadable file. (Initially as `.txt`, can be upgraded to `.docx`).

## Phase 5: AI-Powered Comprehensive Summary (Future)

- [ ] **Task 9: Integrate LLM for Comprehensive Analysis**
  - [ ] Re-enable and configure the `LLMService`.
  - [ ] Create a sophisticated prompt to generate a comprehensive summary from the extracted text.
  - [ ] Update the analysis endpoint to call the LLM and store the structured JSON response.
  - [ ] Update the download endpoint to format this JSON into a user-friendly Word document.

## Phase 6: Final Cleanup

- [ ] **Task 10: Restore `__init__.py`**
  - [ ] Rename `backend/__init__.py.bak` back to `backend/__init__.py`.
  - [ ] Methodically clean up the `__init__.py` files across the application to remove legacy code and only import what is necessary for the new functionality.

## Phase 5: FastAPI Backend Foundation (Week 1)

### 1.1 Project Structure Setup
```
src/
├── api/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── cases.py            # Tier 1: Raw data endpoints
│   │   ├── analysis.py         # Tier 2: Analysis endpoints
│   │   └── export.py           # Tier 3: Export endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py         # Request schemas
│   │   └── responses.py        # Response schemas
│   ├── dependencies/
│   │   ├── __init__.py
│   │   └── services.py         # Service dependency injection
│   └── middleware/
│       ├── __init__.py
│       ├── cors.py             # CORS configuration
│       └── logging.py          # Request logging
```

### 1.2 Dependencies Installation
```bash
# Add to requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
aiofiles==23.2.1
```

### 1.3 Core FastAPI Application
```python
# src/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import cases, analysis, export

app = FastAPI(
    title="Legal Assistant API",
    description="API for Kenyan legal case analysis and research",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cases.router, prefix="/api/v1/cases", tags=["cases"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(export.router, prefix="/api/v1/export", tags=["export"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

## Phase 6: Tier 1 - Raw Data Layer (Week 2-3)

### 2.1 Case Search Endpoint
```python
# src/api/routers/cases.py
from fastapi import APIRouter, Query, HTTPException
from ..models.requests import SearchRequest
from ..models.responses import SearchResponse
from ...services.serp_search_service import SerpSearchService

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
async def search_cases(request: SearchRequest):
    """Search for legal cases using natural language queries"""
    try:
        search_service = SerpSearchService()
        results = await search_service.search_cases(
            query=request.query,
            max_results=request.max_results,
            court_level=request.court_level
        )
        return SearchResponse(
            success=True,
            results=results,
            total_count=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_cases_get(
    query: str = Query(..., description="Search query"),
    max_results: int = Query(10, ge=1, le=100),
    court_level: str = Query(None, description="Court level filter")
):
    """GET endpoint for case search"""
    # Similar implementation as POST
```

### 2.2 PDF Download Management
```python
@router.post("/download")
async def download_case_pdfs(case_urls: List[str]):
    """Download PDFs for specified case URLs"""
    try:
        downloader = PDFDownloader()
        results = []
        for url in case_urls:
            result = await downloader.download_pdf(url)
            results.append(result)
        return {"success": True, "downloads": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{case_id}/status")
async def get_download_status(case_id: str):
    """Get download status for a specific case"""
    # Implementation for tracking download progress
```

### 2.3 Raw Case Data Access
```python
@router.get("/raw")
async def get_raw_cases(
    court_level: str = Query(None),
    date_from: str = Query(None),
    date_to: str = Query(None),
    limit: int = Query(50, ge=1, le=1000)
):
    """Get raw case data with filtering options"""
    # Implementation for accessing cached case data

@router.get("/raw/{case_id}")
async def get_case_metadata(case_id: str):
    """Get metadata for a specific case"""
    # Implementation for case metadata retrieval

@router.get("/raw/{case_id}/pdf")
async def get_case_pdf(case_id: str, pdf_type: str = "standard"):
    """Serve PDF file for a specific case"""
    # Implementation for PDF file serving
```

### 2.4 Pleadings Management
```python
@router.get("/pleadings/{case_id}")
async def get_case_pleadings(case_id: str):
    """Get extracted pleadings for a specific case"""
    try:
        # Integrate with existing pleadings analysis service
        pleadings_service = PDFAnalysisService()
        pleadings = await pleadings_service.extract_pleadings(case_id)
        return {"success": True, "pleadings": pleadings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 2.5 User Upload Functionality
```python
from fastapi import UploadFile, File, Form

@router.post("/upload")
async def upload_case(
    file: UploadFile = File(...),
    case_title: str = Form(...),
    court_level: str = Form(...),
    case_number: str = Form(None)
):
    """Upload a new case PDF with metadata"""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files allowed")

        # Save file and process
        # Implementation for file upload and processing
        return {"success": True, "case_id": "generated_id"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Phase 7: Tier 2 - Analysis Layer (Week 4-5)

### 3.1 Analysis Endpoints
```python
# src/api/routers/analysis.py
from fastapi import APIRouter, HTTPException
from ...services.case_analyzer import CaseAnalyzer
from ...services.pdf_analysis_service import PDFAnalysisService

router = APIRouter()

@router.get("/pleadings/{case_id}")
async def analyze_pleadings(case_id: str):
    """Analyze pleadings for a specific case"""
    try:
        analyzer = PDFAnalysisService()
        analysis = await analyzer.analyze_pleadings(case_id)
        return {"success": True, "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rulings/{case_id}")
async def analyze_rulings(case_id: str):
    """Analyze court rulings for a specific case"""
    # Implementation for rulings analysis

@router.get("/summaries/{case_id}")
async def get_case_summary(case_id: str):
    """Get comprehensive case summary"""
    # Implementation for case summary

@router.get("/litigation-hops/{case_id}")
async def get_litigation_hops(case_id: str):
    """Get litigation progression across court levels"""
    # Implementation for litigation hop analysis

@router.get("/relationships/{case_id}")
async def get_case_relationships(case_id: str):
    """Get related cases and precedents"""
    # Implementation for case relationships
```

## Phase 8: Tier 3 - Application Layer (Week 6)

### 4.1 Export Functionality
```python
# src/api/routers/export.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from ...services.result_formatter import ResultFormatter

router = APIRouter()

@router.post("/pdf")
async def export_pdf_report(case_ids: List[str], report_type: str = "comprehensive"):
    """Generate and download PDF report"""
    try:
        formatter = ResultFormatter()
        pdf_path = await formatter.generate_pdf_report(case_ids, report_type)
        return FileResponse(pdf_path, filename=f"legal_report_{datetime.now().strftime('%Y%m%d')}.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/json")
async def export_json_data(case_ids: List[str]):
    """Export case data in JSON format"""
    # Implementation for JSON export

@router.post("/csv")
async def export_csv_data(case_ids: List[str]):
    """Export case data in CSV format"""
    # Implementation for CSV export
```

## Phase 9: React Frontend Foundation (Week 8)

### 5.1 Project Setup
```bash
# Create React TypeScript project
npx create-react-app frontend --template typescript
cd frontend

# Install dependencies
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material
npm install react-router-dom
npm install axios
npm install @reduxjs/toolkit react-redux
npm install react-pdf
npm install @types/react-pdf
```

### 5.2 Project Structure
```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Loading.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   ├── search/
│   │   │   ├── SearchForm.tsx
│   │   │   ├── SearchResults.tsx
│   │   │   └── FilterPanel.tsx
│   │   ├── cases/
│   │   │   ├── CaseOverview.tsx
│   │   │   ├── CaseAnalysis.tsx
│   │   │   └── PDFViewer.tsx
│   │   └── export/
│   │       ├── ReportBuilder.tsx
│   │       └── ExportOptions.tsx
│   ├── pages/
│   │   ├── Home.tsx
│   │   ├── Search.tsx
│   │   ├── CaseDetail.tsx
│   │   └── Export.tsx
│   ├── services/
│   │   ├── api.ts
│   │   ├── searchService.ts
│   │   ├── caseService.ts
│   │   └── exportService.ts
│   ├── store/
│   │   ├── index.ts
│   │   ├── searchSlice.ts
│   │   └── caseSlice.ts
│   ├── types/
│   │   ├── api.ts
│   │   ├── search.ts
│   │   └── cases.ts
│   └── utils/
│       ├── constants.ts
│       └── helpers.ts
```

### 5.3 API Service Layer
```typescript
// src/services/api.ts
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth headers here when implemented
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle common errors
    if (error.response?.status === 500) {
      console.error('Server error:', error.response.data);
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 5.4 Search Service
```typescript
// src/services/searchService.ts
import api from './api';
import { SearchRequest, SearchResponse } from '../types/search';

export const searchService = {
  async searchCases(request: SearchRequest): Promise<SearchResponse> {
    const response = await api.post('/api/v1/cases/search', request);
    return response.data;
  },

  async searchCasesGet(query: string, maxResults: number = 10): Promise<SearchResponse> {
    const response = await api.get('/api/v1/cases/search', {
      params: { query, max_results: maxResults }
    });
    return response.data;
  }
};
```

## Phase 10: Search & Discovery Interface (Week 9)

### 6.1 Search Form Component
```typescript
// src/components/search/SearchForm.tsx
import React, { useState } from 'react';
import {
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography
} from '@mui/material';
import { SearchRequest } from '../../types/search';

interface SearchFormProps {
  onSearch: (request: SearchRequest) => void;
  loading: boolean;
}

export const SearchForm: React.FC<SearchFormProps> = ({ onSearch, loading }) => {
  const [query, setQuery] = useState('');
  const [maxResults, setMaxResults] = useState(10);
  const [courtLevel, setCourtLevel] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch({
      query,
      max_results: maxResults,
      court_level: courtLevel || undefined
    });
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
      <Typography variant="h5" gutterBottom>
        Search Legal Cases
      </Typography>

      <TextField
        fullWidth
        label="Search Query"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter your legal research query..."
        margin="normal"
        required
      />

      <FormControl fullWidth margin="normal">
        <InputLabel>Court Level</InputLabel>
        <Select
          value={courtLevel}
          onChange={(e) => setCourtLevel(e.target.value)}
        >
          <MenuItem value="">All Courts</MenuItem>
          <MenuItem value="magistrate">Magistrate Court</MenuItem>
          <MenuItem value="high">High Court</MenuItem>
          <MenuItem value="appellate">Court of Appeal</MenuItem>
        </Select>
      </FormControl>

      <TextField
        fullWidth
        type="number"
        label="Max Results"
        value={maxResults}
        onChange={(e) => setMaxResults(Number(e.target.value))}
        margin="normal"
        inputProps={{ min: 1, max: 100 }}
      />

      <Button
        type="submit"
        fullWidth
        variant="contained"
        disabled={loading || !query}
        sx={{ mt: 3, mb: 2 }}
      >
        {loading ? 'Searching...' : 'Search Cases'}
      </Button>
    </Box>
  );
};
```

### 6.2 Search Results Component
```typescript
// src/components/search/SearchResults.tsx
import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  Box
} from '@mui/material';
import { SearchResult } from '../../types/search';

interface SearchResultsProps {
  results: SearchResult[];
  onCaseSelect: (caseId: string) => void;
  onDownload: (caseId: string) => void;
}

export const SearchResults: React.FC<SearchResultsProps> = ({
  results,
  onCaseSelect,
  onDownload
}) => {
  return (
    <Grid container spacing={2}>
      {results.map((result, index) => (
        <Grid item xs={12} md={6} key={index}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {result.title}
              </Typography>

              <Box sx={{ mb: 2 }}>
                <Chip
                  label={result.appellate_court.court}
                  color="primary"
                  size="small"
                  sx={{ mr: 1 }}
                />
                <Chip
                  label={result.confidence}
                  color="secondary"
                  size="small"
                />
              </Box>

              <Typography variant="body2" color="text.secondary" paragraph>
                {result.description}
              </Typography>

              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => onCaseSelect(result.appellate_court.url)}
                >
                  View Details
                </Button>
                <Button
                  size="small"
                  variant="contained"
                  onClick={() => onDownload(result.appellate_court.url)}
                >
                  Download PDF
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};
```

## Best Starting Points

### For FastAPI Backend:
1. **Start with `/api/v1/cases/search`** - Leverages existing SerpSearchService
2. **Then add `/api/v1/cases/download`** - Integrates PDFDownloader service
3. **Follow with `/api/v1/cases/raw`** - Provides access to cached data

### For React Frontend:
1. **Start with Search Interface** - Most critical user-facing feature
2. **Then add Case Analysis Dashboard** - Core value proposition
3. **Follow with Export Interface** - Completes the user workflow

## Development Workflow

### Backend Development
1. Create FastAPI application structure
2. Implement health check endpoint
3. Add first endpoint (`/api/v1/cases/search`)
4. Test with existing services
5. Add remaining Tier 1 endpoints
6. Implement Tier 2 and Tier 3 endpoints
7. Add comprehensive error handling
8. Generate API documentation

### Frontend Development
1. Set up React TypeScript project
2. Create basic layout components
3. Implement search interface
4. Add case analysis dashboard
5. Implement PDF viewer
6. Add export functionality
7. Test integration with backend
8. Optimize performance and UX

### Integration Testing
1. Test API endpoints with real data
2. Validate frontend-backend communication
3. Test file upload/download functionality
4. Verify PDF viewing capabilities
5. Test export functionality
6. Performance testing and optimization

This implementation plan provides a structured approach to building the FastAPI backend and React frontend while leveraging your existing robust backend services.