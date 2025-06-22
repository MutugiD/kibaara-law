#!/bin/bash
echo "--- Activating Virtual Environment ---"
source law_env/bin/activate

echo "--- Installing/Updating Dependencies ---"
pip install --upgrade pip
pip install "fastapi[all]" uvicorn loguru sqlalchemy

echo "--- Starting FastAPI Server ---"
uvicorn backend.api.main:app --host 0.0.0.0 --port 8080