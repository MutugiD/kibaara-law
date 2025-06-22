/**
 * Search results component for displaying legal case search results
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Link,
  CircularProgress,
  Alert,
  Grid,
} from '@mui/material';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import { SearchResult } from '../../types/api';

const SearchResults: React.FC = () => {
  const { results, loading, error } = useSelector((state: RootState) => state.search);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!results || results.length === 0) {
    return (
      <Alert severity="info">
        No cases found. Try adjusting your search criteria.
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Search Results ({results.length} cases found)
      </Typography>

      <Grid container spacing={3}>
        {results.map((result: SearchResult, index: number) => (
          <Grid item xs={12} key={index}>
            <Card elevation={2}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {result.title}
                </Typography>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {result.description}
                  </Typography>
                </Box>

                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" color="primary" gutterBottom>
                      Appellate Court
                    </Typography>
                    <Typography variant="body2">
                      <strong>Court:</strong> {result.appellate_court.court}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Case Number:</strong> {result.appellate_court.case_number}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Date:</strong> {result.appellate_court.date}
                    </Typography>
                    {result.appellate_court.url && (
                      <Link href={result.appellate_court.url} target="_blank" rel="noopener">
                        View Case
                      </Link>
                    )}
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" color="primary" gutterBottom>
                      Trial Court Reference
                    </Typography>
                    <Typography variant="body2">
                      <strong>Court:</strong> {result.trial_reference.court}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Case Number:</strong> {result.trial_reference.case_number}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Date:</strong> {result.trial_reference.date}
                    </Typography>
                  </Grid>
                </Grid>

                <Box sx={{ mt: 2 }}>
                  <Chip
                    label={`Confidence: ${result.confidence}`}
                    size="small"
                    color="secondary"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default SearchResults;