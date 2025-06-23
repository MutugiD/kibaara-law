#!/bin/bash

# Kibaara Law Assistant Frontend Startup Script

echo "Starting Kibaara Law Assistant Frontend..."

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Check if backend is running
echo "Checking if backend is running..."
if curl -s http://localhost:8080/api/v1/cases/ > /dev/null 2>&1; then
    echo "✅ Backend is running on http://localhost:8080"
else
    echo "⚠️  Warning: Backend does not appear to be running on http://localhost:8080"
    echo "   Please start the FastAPI backend first using: ./start_server.sh"
    echo "   Continuing anyway..."
fi

# Start the frontend server
echo "Starting frontend server on http://localhost:3000..."
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev