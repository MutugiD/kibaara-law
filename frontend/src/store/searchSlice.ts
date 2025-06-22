/**
 * Redux slice for search functionality
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { SearchRequest, SearchResponse, SearchResult } from '../types/api';
import { searchCases, searchCasesGet } from '../services/api';

export interface SearchState {
  results: SearchResult[];
  loading: boolean;
  error: string | null;
  lastQuery: string;
  totalCount: number;
  lastSearchTimestamp: string | null;
}

const initialState: SearchState = {
  results: [],
  loading: false,
  error: null,
  lastQuery: '',
  totalCount: 0,
  lastSearchTimestamp: null,
};

// Async thunk for searching cases
export const searchCasesAsync = createAsyncThunk(
  'search/searchCases',
  async (request: SearchRequest, { rejectWithValue }) => {
    try {
      const response = await searchCases(request);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || error.message || 'Search failed');
    }
  }
);

// Async thunk for searching cases using GET method
export const searchCasesGetAsync = createAsyncThunk(
  'search/searchCasesGet',
  async (
    { query, maxResults, courtLevel }: { query: string; maxResults: number; courtLevel?: string },
    { rejectWithValue }
  ) => {
    try {
      const response = await searchCasesGet(query, maxResults, courtLevel);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || error.message || 'Search failed');
    }
  }
);

const searchSlice = createSlice({
  name: 'search',
  initialState,
  reducers: {
    clearSearch: (state) => {
      state.results = [];
      state.error = null;
      state.lastQuery = '';
      state.totalCount = 0;
      state.lastSearchTimestamp = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // searchCasesAsync
      .addCase(searchCasesAsync.pending, (state, action) => {
        state.loading = true;
        state.error = null;
        state.lastQuery = action.meta.arg.query;
      })
      .addCase(searchCasesAsync.fulfilled, (state, action: PayloadAction<SearchResponse>) => {
        state.loading = false;
        state.results = action.payload.results;
        state.totalCount = action.payload.total_count;
        state.lastSearchTimestamp = action.payload.timestamp;
        state.error = null;
      })
      .addCase(searchCasesAsync.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
        state.results = [];
        state.totalCount = 0;
      })
      // searchCasesGetAsync
      .addCase(searchCasesGetAsync.pending, (state, action) => {
        state.loading = true;
        state.error = null;
        state.lastQuery = action.meta.arg.query;
      })
      .addCase(searchCasesGetAsync.fulfilled, (state, action: PayloadAction<SearchResponse>) => {
        state.loading = false;
        state.results = action.payload.results;
        state.totalCount = action.payload.total_count;
        state.lastSearchTimestamp = action.payload.timestamp;
        state.error = null;
      })
      .addCase(searchCasesGetAsync.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
        state.results = [];
        state.totalCount = 0;
      });
  },
});

export const { clearSearch, clearError } = searchSlice.actions;
export default searchSlice.reducer;