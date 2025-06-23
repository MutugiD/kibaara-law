const express = require('express');
const multer = require('multer');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// FastAPI backend URL
const BACKEND_URL = 'http://localhost:8080';

// Configure multer for file uploads
const upload = multer({ dest: 'uploads/' });

// Set up EJS as templating engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Routes
app.get('/', async (req, res) => {
    try {
        res.render('pages/upload', {
            title: 'Upload Case File',
            message: req.query.message || null,
            error: req.query.error || null
        });
    } catch (error) {
        console.error('Error rendering upload page:', error);
        res.status(500).render('pages/upload', {
            title: 'Upload Case File',
            error: 'Failed to load upload page'
        });
    }
});

app.post('/upload', upload.single('file'), async (req, res) => {
    try {
        if (!req.file) {
            return res.redirect('/?error=No file selected');
        }

        const formData = new FormData();
        formData.append('file', req.file);
        formData.append('document_type', req.body.document_type || 'PLEADINGS');

        const response = await axios.post(`${BACKEND_URL}/api/v1/cases/upload`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });

        res.redirect('/?message=File uploaded successfully');
    } catch (error) {
        console.error('Upload error:', error.response?.data || error.message);
        res.redirect(`/?error=Upload failed: ${error.response?.data?.detail || error.message}`);
    }
});

app.get('/processing', async (req, res) => {
    try {
        const response = await axios.get(`${BACKEND_URL}/api/v1/cases/`);
        const cases = response.data;

        res.render('pages/processing', {
            title: 'Case Processing',
            cases: cases,
            message: req.query.message || null,
            error: req.query.error || null
        });
    } catch (error) {
        console.error('Error fetching cases:', error);
        res.render('pages/processing', {
            title: 'Case Processing',
            cases: [],
            error: 'Failed to load cases'
        });
    }
});

app.post('/analyze/:filename', async (req, res) => {
    try {
        const { filename } = req.params;
        await axios.post(`${BACKEND_URL}/api/v1/cases/analyze/${filename}`);
        res.redirect('/processing?message=Analysis started successfully');
    } catch (error) {
        console.error('Analysis error:', error.response?.data || error.message);
        res.redirect(`/processing?error=Analysis failed: ${error.response?.data?.detail || error.message}`);
    }
});

app.get('/downloads', async (req, res) => {
    try {
        const response = await axios.get(`${BACKEND_URL}/api/v1/cases/`);
        const cases = response.data;

        res.render('pages/downloads', {
            title: 'Download Analysis Results',
            cases: cases,
            backendUrl: BACKEND_URL,
            error: null
        });
    } catch (error) {
        console.error('Error fetching cases for downloads:', error);
        res.render('pages/downloads', {
            title: 'Download Analysis Results',
            cases: [],
            backendUrl: BACKEND_URL,
            error: 'Failed to load cases'
        });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`Frontend server running on http://localhost:${PORT}`);
    console.log(`Backend URL: ${BACKEND_URL}`);
});