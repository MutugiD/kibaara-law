import React, { useState } from 'react';
import { Typography, Container, Paper, Button, Box, Alert, CircularProgress } from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { uploadCase } from '../../services/api';

const VisuallyHiddenInput = styled('input')({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  bottom: 0,
  left: 0,
  whiteSpace: 'nowrap',
  width: 1,
});

const UploadPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
      setSuccess(null);
      setError(null);
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await uploadCase(selectedFile);
      setSuccess(`File "${response.filename}" uploaded successfully! Case ID: ${response.id}`);
      setSelectedFile(null);
    } catch (err) {
      setError('File upload failed. Please ensure it is a valid PDF and try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Upload New Case File
        </Typography>
        <Box sx={{ mt: 3 }}>
          <Button
            component="label"
            variant="contained"
            startIcon={<CloudUploadIcon />}
          >
            Select PDF File
            <VisuallyHiddenInput type="file" accept="application/pdf" onChange={handleFileChange} />
          </Button>
          {selectedFile && (
            <Typography sx={{ mt: 2, fontStyle: 'italic' }}>
              Selected: {selectedFile.name}
            </Typography>
          )}
        </Box>
        <Box sx={{ mt: 3 }}>
          <Button
            variant="contained"
            color="primary"
            disabled={!selectedFile || loading}
            onClick={handleSubmit}
            sx={{ minWidth: 120 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Upload Case'}
          </Button>
        </Box>
        <Box sx={{ mt: 3 }}>
          {success && <Alert severity="success">{success}</Alert>}
          {error && <Alert severity="error">{error}</Alert>}
        </Box>
      </Paper>
    </Container>
  );
};

export default UploadPage;