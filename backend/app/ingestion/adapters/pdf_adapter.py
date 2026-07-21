"""PDF document adapter.

Extracts text and tables from PDF files using pdfplumber.
Falls back to basic extraction if pdfplumber is not available.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.ingestion.adapters.base import (
    DocumentAdapter,
    ExtractedPage,
    ExtractionResult,
)

logger = logging.getLogger(__name__)


class PDFAdapter(DocumentAdapter):
    """Extracts content from PDF documents."""

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        return (".pdf",)

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions

    def extract(self, file_path: Path) -> ExtractionResult:
        """Extract text and tables from a PDF file.

        Strategy:
        1. Try pdfplumber (best for text + tables)
        2. Fall back to PyPDF2 (text only)
        3. Fall back to raw text extraction
        """
        try:
            return self._extract_with_pdfplumber(file_path)
        except ImportError:
            logger.info("pdfplumber not available, trying PyPDF2")
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")

        try:
            return self._extract_with_pypdf2(file_path)
        except ImportError:
            logger.info("PyPDF2 not available")
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {e}")

        return ExtractionResult(
            pages=(),
            total_pages=0,
            extraction_method="failed",
            errors=(f"No PDF library available for {file_path.name}",),
        )

    def _extract_with_pdfplumber(self, file_path: Path) -> ExtractionResult:
        import pdfplumber

        pages: list[ExtractedPage] = []
        errors: list[str] = []

        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                try:
                    text = page.extract_text() or ""
                    tables_raw = page.extract_tables() or []
                    tables = tuple(
                        [row for row in table if row]
                        for table in tables_raw
                        if table
                    )
                    pages.append(ExtractedPage(
                        page_number=i + 1,
                        text=text,
                        tables=tables,
                    ))
                except Exception as e:
                    errors.append(f"Page {i + 1}: {e}")
                    pages.append(ExtractedPage(
                        page_number=i + 1,
                        text="",
                        metadata={"error": str(e)},
                    ))

        return ExtractionResult(
            pages=tuple(pages),
            total_pages=len(pages),
            extraction_method="pdfplumber",
            errors=tuple(errors),
        )

    def _extract_with_pypdf2(self, file_path: Path) -> ExtractionResult:
        from PyPDF2 import PdfReader

        reader = PdfReader(str(file_path))
        pages: list[ExtractedPage] = []
        errors: list[str] = []

        for i, page in enumerate(reader.pages):
            try:
                text = page.extract_text() or ""
                pages.append(ExtractedPage(
                    page_number=i + 1,
                    text=text,
                ))
            except Exception as e:
                errors.append(f"Page {i + 1}: {e}")
                pages.append(ExtractedPage(
                    page_number=i + 1,
                    text="",
                    metadata={"error": str(e)},
                ))

        return ExtractionResult(
            pages=tuple(pages),
            total_pages=len(pages),
            extraction_method="pypdf2",
            errors=tuple(errors),
        )
