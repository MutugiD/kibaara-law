/**
 * API service for communicating with the FastAPI backend
 */

import axios, { AxiosResponse } from 'axios';
import {
  SearchRequest,
  SearchResponse,
  DownloadRequest,
  DownloadResponse,
  CaseMetadataResponse
} from '../types/api';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout
});

// Request interceptor for logging and error handling
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    if (error.response) {
      console.error('Error data:', error.response.data);
      console.error('Error status:', error.response.status);
    }
    return Promise.reject(error);
  }
);

/**
 * Search for legal cases
 */
export const searchCases = async (request: SearchRequest): Promise<SearchResponse> => {
  try {
    const response = await apiClient.post<SearchResponse>('/api/v1/cases/search', request);
    return response.data;
  } catch (error) {
    console.error('Search cases error:', error);
    throw error;
  }
};

/**
 * Search for legal cases using GET method
 */
export const searchCasesGet = async (
  query: string,
  maxResults: number = 10,
  courtLevel?: string
): Promise<SearchResponse> => {
  try {
    const params = new URLSearchParams({
      query,
      max_results: maxResults.toString(),
    });

    if (courtLevel) {
      params.append('court_level', courtLevel);
    }

    const response = await apiClient.get<SearchResponse>(`/api/v1/cases/search?${params}`);
    return response.data;
  } catch (error) {
    console.error('Search cases GET error:', error);
    throw error;
  }
};

/**
 * Download PDFs for specified case URLs
 */
export const downloadCasePDFs = async (request: DownloadRequest): Promise<DownloadResponse> => {
  try {
    const response = await apiClient.post<DownloadResponse>('/api/v1/cases/download', request);
    return response.data;
  } catch (error) {
    console.error('Download PDFs error:', error);
    throw error;
  }
};

/**
 * Get raw case data with filtering options
 */
export const getRawCases = async (
  courtLevel?: string,
  dateFrom?: string,
  dateTo?: string,
  limit: number = 50
): Promise<CaseMetadataResponse> => {
  try {
    const params = new URLSearchParams({
      limit: limit.toString(),
    });

    if (courtLevel) {
      params.append('court_level', courtLevel);
    }
    if (dateFrom) {
      params.append('date_from', dateFrom);
    }
    if (dateTo) {
      params.append('date_to', dateTo);
    }

    const response = await apiClient.get<CaseMetadataResponse>(`/api/v1/cases/raw?${params}`);
    return response.data;
  } catch (error) {
    console.error('Get raw cases error:', error);
    throw error;
  }
};

/**
 * Health check endpoint
 */
export const healthCheck = async (): Promise<any> => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check error:', error);
    throw error;
  }
};

export const uploadCase = async (file: File): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await apiClient.post('/api/v1/cases/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading case:', error);
    throw error;
  }
};

export const getCases = async (): Promise<any[]> => {
  try {
    const response = await apiClient.get('/api/v1/cases/');
    return response.data;
  } catch (error) {
    console.error('Error fetching cases:', error);
    throw error;
  }
};

export default apiClient;