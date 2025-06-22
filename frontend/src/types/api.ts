/**
 * TypeScript interfaces for API requests and responses
 */

export interface SearchRequest {
  query: string;
  max_results: number;
  court_level?: string;
}

export interface AppellateCourt {
  court: string;
  case_number: string;
  date: string;
  url: string;
}

export interface TrialReference {
  court: string;
  case_number: string;
  date: string;
}

export interface SearchResult {
  title: string;
  appellate_court: AppellateCourt;
  trial_reference: TrialReference;
  description: string;
  confidence: string;
}

export interface SearchResponse {
  success: boolean;
  results: SearchResult[];
  total_count: number;
  query: string;
  timestamp: string;
}

export interface DownloadRequest {
  case_urls: string[];
}

export interface PDFFile {
  filename: string;
  filepath: string;
  type: string;
  url: string;
  size: number;
  cached: boolean;
}

export interface DownloadResult {
  case_title: string;
  success: boolean;
  pdfs_downloaded: number;
  total_pdfs_found: number;
  pdf_files: PDFFile[];
  appellate_url: string;
  download_timestamp: string;
  error?: string;
}

export interface DownloadResponse {
  success: boolean;
  downloads: DownloadResult[];
  total_cases: number;
  successful_downloads: number;
  failed_downloads: number;
  timestamp: string;
}

export interface CaseMetadata {
  case_id: string;
  title: string;
  court_level: string;
  case_number: string;
  date: string;
  url: string;
  has_pdf: boolean;
  pdf_count: number;
  cached_at?: string;
}

export interface CaseMetadataResponse {
  success: boolean;
  cases: CaseMetadata[];
  total_count: number;
  filters_applied: Record<string, any>;
  timestamp: string;
}

export interface ErrorResponse {
  success: false;
  error: string;
  error_code?: string;
  timestamp: string;
}

export interface CaseSchema {
  id: number;
  filename: string;
  upload_date: string; // or Date, if you parse it
  status: string;
  analysis_results: any | null;
}