"""PDF document adapter.

Extracts text from PDF files using pypdf.
Includes detection for image-only/scanned PDFs.
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
        """Extract text from a PDF file using pypdf."""
        try:
            return self._extract_with_pypdf(file_path)
        except Exception as e:
            logger.warning(f"pypdf extraction failed: {e}")
            return ExtractionResult(
                pages=(),
                total_pages=0,
                extraction_method="failed",
                errors=(f"Failed to extract text from PDF {file_path.name}: {e}",),
            )

    def _extract_with_pypdf(self, file_path: Path) -> ExtractionResult:
        try:
            from pypdf import PdfReader
        except ImportError:
            return ExtractionResult(
                pages=(),
                total_pages=0,
                extraction_method="failed",
                errors=(f"pypdf library not installed. Cannot process {file_path.name}.",),
            )

        reader = PdfReader(str(file_path))
        pages: list[ExtractedPage] = []
        errors: list[str] = []
        
        total_text_length = 0
        total_pages = len(reader.pages)

        for i, page in enumerate(reader.pages):
            try:
                text = page.extract_text() or ""
                clean_text = text.strip()
                total_text_length += len(clean_text)
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

        if total_pages > 0 and total_text_length == 0:
            errors.append("OCR not supported: The PDF appears to be scanned or image-only.")

        return ExtractionResult(
            pages=tuple(pages),
            total_pages=total_pages,
            extraction_method="pypdf",
            errors=tuple(errors),
        )
