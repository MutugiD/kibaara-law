/**
 * Search form component for legal case search
 */

import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Paper,
  Alert,
  Grid,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../store';
import { searchCasesGetAsync, clearError } from '../../store/searchSlice';

const SearchForm: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { loading, error } = useSelector((state: RootState) => state.search);

  const [query, setQuery] = useState('');
  const [maxResults, setMaxResults] = useState(10);
  const [courtLevel, setCourtLevel] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    dispatch(clearError());
    dispatch(
      searchCasesGetAsync({
        query: query.trim(),
        maxResults,
        courtLevel: courtLevel || undefined,
      })
    );
  };

  const handleClear = () => {
    setQuery('');
    setMaxResults(10);
    setCourtLevel('');
    dispatch(clearError());
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h5" gutterBottom>
        Search Legal Cases
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => dispatch(clearError())}>
          {error}
        </Alert>
      )}

      <Box component="form" onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Search Query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your legal research query..."
              required
              disabled={loading}
              helperText="Enter keywords, case names, or legal concepts to search for"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth disabled={loading}>
              <InputLabel>Court Level</InputLabel>
              <Select
                value={courtLevel}
                onChange={(e) => setCourtLevel(e.target.value)}
                label="Court Level"
              >
                <MenuItem value="">All Courts</MenuItem>
                <MenuItem value="magistrate">Magistrate Court</MenuItem>
                <MenuItem value="high">High Court</MenuItem>
                <MenuItem value="appellate">Court of Appeal</MenuItem>
                <MenuItem value="supreme">Supreme Court</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="number"
              label="Max Results"
              value={maxResults}
              onChange={(e) => setMaxResults(Number(e.target.value))}
              inputProps={{ min: 1, max: 100 }}
              disabled={loading}
              helperText="Maximum number of results to return (1-100)"
            />
          </Grid>

          <Grid item xs={12}>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button
                variant="outlined"
                onClick={handleClear}
                disabled={loading}
              >
                Clear
              </Button>
              <Button
                type="submit"
                variant="contained"
                disabled={loading || !query.trim()}
                sx={{ minWidth: 120 }}
              >
                {loading ? 'Searching...' : 'Search Cases'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
};

export default SearchForm;