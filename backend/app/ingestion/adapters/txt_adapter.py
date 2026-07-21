"""Plain text document adapter.

Handles .txt and .md files. Simple and robust.
"""
from __future__ import annotations

import logging
from pathlib import Path

from app.ingestion.adapters.base import (
    DocumentAdapter,
    ExtractedPage,
    ExtractionResult,
)

logger = logging.getLogger(__name__)


class TXTAdapter(DocumentAdapter):
    """Extracts content from plain text files."""

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        return (".txt", ".md", ".text", ".log")

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions

    def extract(self, file_path: Path) -> ExtractionResult:
        try:
            raw = file_path.read_bytes()
            for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
                try:
                    text = raw.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                text = raw.decode("utf-8", errors="replace")

            page = ExtractedPage(
                page_number=1,
                text=text,
                metadata={"char_count": len(text)},
            )

            return ExtractionResult(
                pages=(page,),
                total_pages=1,
                extraction_method="text_extraction",
            )
        except Exception as e:
            return ExtractionResult(
                pages=(),
                total_pages=0,
                extraction_method="failed",
                errors=(str(e),),
            )
