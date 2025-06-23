"""
This service contains the core business logic for interacting with the case data.
It provides functions to create, retrieve, and manage cases in the database.
"""
from sqlalchemy.orm import Session
from loguru import logger
from typing import Optional
from pathlib import Path

from backend.models import case_models
from backend.pdf_processor.pdf_extractor import PDFExtractor

UPLOADS_DIR = Path("data/raw")


def create_case(db: Session, filename: str, document_type: case_models.DocumentType) -> case_models.Case:
    """
    Creates a new case record in the database.

    Args:
        db: The database session.
        filename: The name of the uploaded file.
        document_type: The type of the document being uploaded.

    Returns:
        The newly created Case object.
    """
    logger.info(f"--- SERVICE: create_case called with filename: {filename}, type: {document_type} ---")
    try:
        db_case = case_models.Case(
            filename=filename,
            document_type=document_type.value,
            status=case_models.CaseStatus.UPLOADED.value,
            analysis_results=None
        )
        logger.info(f"Created Case model instance: {db_case}")
        db.add(db_case)
        logger.info("Added instance to session.")
        db.commit()
        logger.info("Committed session.")
        db.refresh(db_case)
        logger.info(f"Refreshed instance. Returning case ID: {db_case.id}")
        return db_case
    except Exception as e:
        logger.error(f"--- SERVICE FAILED: Exception during DB operation: {e} ---")
        import traceback
        logger.error(traceback.format_exc())
        raise


def get_all_cases(db: Session, skip: int = 0, limit: int = 100) -> list[case_models.Case]:
    """
    Retrieves a list of all cases from the database.

    Args:
        db: The database session.
        skip: The number of records to skip for pagination.
        limit: The maximum number of records to return.

    Returns:
        A list of Case objects.
    """
    logger.info(f"Retrieving all cases with skip={skip} and limit={limit}")
    return db.query(case_models.Case).offset(skip).limit(limit).all()


def get_case_by_id(db: Session, case_id: int) -> Optional[case_models.Case]:
    """
    Retrieves a single case by its ID.
    """
    return db.query(case_models.Case).filter(case_models.Case.id == case_id).first()


def get_case_by_filename(db: Session, filename: str) -> Optional[case_models.Case]:
    """
    Retrieves a single case by its filename.
    """
    return db.query(case_models.Case).filter(case_models.Case.filename == filename).first()


def analyze_case(db: Session, filename: str) -> case_models.Case:
    """
    Analyzes a case by extracting text from its PDF and updates its status.
    """
    db_case = get_case_by_filename(db, filename)
    if not db_case:
        raise ValueError("Case not found")

    logger.info(f"--- SERVICE: Analyzing case file: {filename} ---")
    db_case.status = case_models.CaseStatus.PROCESSING.value
    db.commit()
    db.refresh(db_case)
    logger.info(f"Case {filename} status updated to PROCESSING.")

    # --- Real Analysis Step ---
    file_path = UPLOADS_DIR / filename
    if not file_path.exists():
        db_case.status = case_models.CaseStatus.FAILED.value
        db_case.analysis_results = {"error": f"File not found at {file_path}"}
        db.commit()
        logger.error(f"File not found for analysis: {file_path}")
        raise ValueError(f"File not found: {filename}")

    extractor = PDFExtractor()
    extracted_text = extractor.extract_text_from_pdf(str(file_path))

    if not extracted_text:
        db_case.status = case_models.CaseStatus.FAILED.value
        db_case.analysis_results = {"error": "Failed to extract text from PDF."}
        db.commit()
        logger.error(f"Failed to extract text from {filename}")
        raise ValueError("Text extraction failed.")
    # --- End Analysis Step ---


    db_case.status = case_models.CaseStatus.COMPLETED.value
    db_case.analysis_results = {
        "extracted_text": extracted_text,
    }
    db.commit()
    db.refresh(db_case)
    logger.info(f"--- SERVICE: Case file {filename} analysis COMPLETE ---")

    return db_case