"""
Cases router for handling case uploads, listings, and analysis.
"""
import shutil
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
import aiofiles
from loguru import logger
from sqlalchemy.orm import Session
import io

from backend.database import get_db
from backend.models import case_models
from backend.services import case_service

router = APIRouter()


@router.post("/upload", response_model=case_models.CaseSchema)
async def upload_case_file(
    file: UploadFile = File(...),
    document_type: case_models.DocumentType = Form(...),
    db: Session = Depends(get_db)
):
    """
    Accepts a file and its type, saves it locally, and creates a new case record.
    """
    logger.info(f"--- UPLOAD START: Received file: {file.filename}, type: {document_type} ---")

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    try:
        file_location = Path("data/raw") / file.filename
        logger.info(f"Attempting to save file to: {file_location}")

        async with aiofiles.open(file_location, "wb") as buffer:
            content = await file.read()
            await buffer.write(content)

        logger.info(f"Successfully saved file: {file.filename}")

        logger.info("Calling case_service.create_case...")
        db_case = case_service.create_case(
            db=db, filename=file.filename, document_type=document_type
        )
        logger.info(f"--- UPLOAD SUCCESS: Created case with ID: {db_case.id} ---")

        return db_case
    except Exception as e:
        logger.error(f"--- UPLOAD FAILED: Exception occurred: {e} ---")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Could not upload file: {e}")


@router.post("/analyze/{filename}", response_model=case_models.CaseSchema)
def analyze_case_endpoint(filename: str, db: Session = Depends(get_db)):
    """
    Triggers the analysis of an uploaded case file.
    """
    logger.info(f"--- API: Received request to analyze file: {filename} ---")
    try:
        analyzed_case = case_service.analyze_case(db=db, filename=filename)
        return analyzed_case
    except ValueError as e:
        logger.error(f"--- API: Case not found for filename: {filename} ---")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"--- API: Failed to analyze file {filename}: {e} ---")
        raise HTTPException(status_code=500, detail=f"Could not analyze file: {e}")


@router.get("/download/{filename}", response_class=StreamingResponse)
def download_analysis_file(filename: str, db: Session = Depends(get_db)):
    """
    Downloads the analysis results for a given case file.
    """
    logger.info(f"--- API: Received request to download analysis for: {filename} ---")
    db_case = case_service.get_case_by_filename(db, filename)

    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found.")

    if not db_case.analysis_results or "extracted_text" not in db_case.analysis_results:
        raise HTTPException(status_code=400, detail="Case has not been analyzed yet.")

    extracted_text = db_case.analysis_results["extracted_text"]

    # Create a file-like object in memory
    string_io = io.StringIO(extracted_text)

    # Create a streaming response
    return StreamingResponse(
        iter([string_io.read()]),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={db_case.filename}_analysis.txt"}
    )


@router.get("/", response_model=List[case_models.CaseSchema])
def get_all_cases(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Retrieve a list of all cases from the database.
    """
    cases = case_service.get_all_cases(db, skip=skip, limit=limit)
    # Manually convert each case to the Pydantic schema
    return [case_models.CaseSchema.from_orm(c) for c in cases]