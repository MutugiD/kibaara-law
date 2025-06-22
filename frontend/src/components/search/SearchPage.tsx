/**
 * Main search page component that combines search form and results
 */

import React from 'react';
import { Container, Box, Typography } from '@mui/material';
import SearchForm from './SearchForm';
import SearchResults from './SearchResults';

const SearchPage: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box mb={4}>
        <Typography variant="h3" component="h1" gutterBottom>
          Kenyan Legal Assistant
        </Typography>
        <Typography variant="h6" color="text.secondary" paragraph>
          Search and analyze Kenyan court cases with advanced legal research tools
        </Typography>
      </Box>

      <SearchForm />
      <SearchResults />
    </Container>
  );
};

export default SearchPage;