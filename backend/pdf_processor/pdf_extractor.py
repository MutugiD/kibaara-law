"""
PDF Extractor Module

This module handles the extraction and processing of text content from PDF documents.
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import PyPDF2
from loguru import logger


class PDFExtractor:
    """
    Service for extracting and processing text content from PDF documents.

    This service provides functionality to convert PDFs to readable text,
    clean and structure the content, and extract specific sections.
    """

    def __init__(self, processed_dir: str = "data/processed"):
        """
        Initialize the PDF extractor.

        Args:
            processed_dir: Directory to store processed PDF content
        """
        self.processed_dir = Path(processed_dir)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"PDF Extractor initialized with processed directory: {self.processed_dir}")

    def extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """
        Extract text content from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text content or None if extraction fails
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""

                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += f"\n--- PAGE {page_num + 1} ---\n"
                            text_content += page_text
                            text_content += "\n"
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                        continue

                if text_content.strip():
                    logger.info(f"Successfully extracted text from {pdf_path}")
                    return text_content
                else:
                    logger.warning(f"No text content extracted from {pdf_path}")
                    return None

        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            return None

    def clean_text_content(self, text: str) -> str:
        """
        Clean and normalize extracted text content.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned and normalized text
        """
        if not text:
            return ""

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove page markers
        text = re.sub(r'--- PAGE \d+ ---', '', text)

        # Normalize line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # Remove special characters that might interfere with analysis
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\']', ' ', text)

        # Clean up multiple spaces
        text = re.sub(r' +', ' ', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        logger.debug("Text content cleaned and normalized")
        return text

    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract different sections from the PDF text.

        Args:
            text: Cleaned text content

        Returns:
            Dictionary containing different sections
        """
        sections = {
            'header': '',
            'parties': '',
            'pleadings': '',
            'evidence': '',
            'judgment': '',
            'orders': '',
            'footer': ''
        }

        if not text:
            return sections

        # Split text into paragraphs
        paragraphs = text.split('\n\n')

        current_section = 'header'
        section_content = []

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # Detect section changes based on keywords
            lower_para = paragraph.lower()

            if any(keyword in lower_para for keyword in ['judgment', 'ruling', 'decision', 'held']):
                if section_content:
                    sections[current_section] = '\n\n'.join(section_content)
                current_section = 'judgment'
                section_content = [paragraph]
            elif any(keyword in lower_para for keyword in ['order', 'orders', 'relief', 'award']):
                if section_content:
                    sections[current_section] = '\n\n'.join(section_content)
                current_section = 'orders'
                section_content = [paragraph]
            elif any(keyword in lower_para for keyword in ['plaintiff', 'defendant', 'appellant', 'respondent']):
                if section_content:
                    sections[current_section] = '\n\n'.join(section_content)
                current_section = 'parties'
                section_content = [paragraph]
            elif any(keyword in lower_para for keyword in ['plead', 'claim', 'allege', 'contend']):
                if section_content:
                    sections[current_section] = '\n\n'.join(section_content)
                current_section = 'pleadings'
                section_content = [paragraph]
            elif any(keyword in lower_para for keyword in ['evidence', 'witness', 'exhibit', 'document']):
                if section_content:
                    sections[current_section] = '\n\n'.join(section_content)
                current_section = 'evidence'
                section_content = [paragraph]
            else:
                section_content.append(paragraph)

        # Add the last section
        if section_content:
            sections[current_section] = '\n\n'.join(section_content)

        logger.debug(f"Extracted {len(sections)} sections from PDF text")
        return sections

    def process_pdf_file(self, pdf_path: str, case_title: str) -> Dict[str, any]:
        """
        Process a PDF file and extract structured content.

        Args:
            pdf_path: Path to the PDF file
            case_title: Title of the case for file naming

        Returns:
            Dictionary containing processed content and metadata
        """
        logger.info(f"Processing PDF file: {pdf_path}")

        # Extract raw text
        raw_text = self.extract_text_from_pdf(pdf_path)
        if not raw_text:
            return {
                'success': False,
                'error': 'Failed to extract text from PDF',
                'file_path': pdf_path
            }

        # Clean text
        cleaned_text = self.clean_text_content(raw_text)

        # Extract sections
        sections = self.extract_sections(cleaned_text)

        # Create processed file
        processed_file = self.save_processed_content(
            case_title, cleaned_text, sections, pdf_path
        )

        result = {
            'success': True,
            'file_path': pdf_path,
            'processed_file': processed_file,
            'raw_text': raw_text,
            'cleaned_text': cleaned_text,
            'sections': sections,
            'text_length': len(cleaned_text),
            'word_count': len(cleaned_text.split())
        }

        logger.info(f"Successfully processed PDF: {pdf_path}")
        return result

    def save_processed_content(self, case_title: str, cleaned_text: str,
                             sections: Dict[str, str], original_pdf: str) -> str:
        """
        Save processed content to a text file.

        Args:
            case_title: Title of the case
            cleaned_text: Cleaned text content
            sections: Extracted sections
            original_pdf: Path to original PDF

        Returns:
            Path to the saved processed file
        """
        # Create safe filename
        safe_title = re.sub(r'[^\w\s-]', '', case_title)
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        safe_title = safe_title.strip('-')

        processed_file = self.processed_dir / f"{safe_title}_processed.txt"

        with open(processed_file, 'w', encoding='utf-8') as f:
            f.write(f"PROCESSED PDF CONTENT\n")
            f.write(f"====================\n\n")
            f.write(f"Original PDF: {original_pdf}\n")
            f.write(f"Case Title: {case_title}\n")
            f.write(f"Processing Date: {self._get_timestamp()}\n\n")

            f.write(f"FULL CLEANED TEXT\n")
            f.write(f"=================\n")
            f.write(cleaned_text)
            f.write(f"\n\n")

            f.write(f"EXTRACTED SECTIONS\n")
            f.write(f"==================\n")
            for section_name, section_content in sections.items():
                if section_content:
                    f.write(f"\n{section_name.upper()}:\n")
                    f.write(f"{'=' * len(section_name)}\n")
                    f.write(section_content)
                    f.write(f"\n")

        logger.info(f"Processed content saved to: {processed_file}")
        return str(processed_file)

    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def batch_process_pdfs(self, pdf_directory: str) -> List[Dict[str, any]]:
        """
        Process all PDF files in a directory.

        Args:
            pdf_directory: Directory containing PDF files

        Returns:
            List of processing results
        """
        pdf_dir = Path(pdf_directory)
        if not pdf_dir.exists():
            logger.error(f"PDF directory does not exist: {pdf_directory}")
            return []

        results = []
        pdf_files = list(pdf_dir.glob("*.pdf"))

        logger.info(f"Found {len(pdf_files)} PDF files to process")

        for pdf_file in pdf_files:
            # Extract case title from filename
            case_title = pdf_file.stem

            result = self.process_pdf_file(str(pdf_file), case_title)
            results.append(result)

            if result['success']:
                logger.info(f"Successfully processed: {pdf_file.name}")
            else:
                logger.error(f"Failed to process: {pdf_file.name}")

        logger.info(f"Batch processing completed. {len([r for r in results if r['success']])} successful, {len([r for r in results if not r['success']])} failed")
        return results