"""CSV document adapter.

Extracts structured data from CSV files. Each CSV is
treated as a single-page document with one table.
"""
from __future__ import annotations

import csv
import io
import logging
from pathlib import Path

from app.ingestion.adapters.base import (
    DocumentAdapter,
    ExtractedPage,
    ExtractionResult,
)

logger = logging.getLogger(__name__)


class CSVAdapter(DocumentAdapter):
    """Extracts content from CSV files."""

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        return (".csv",)

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions

    def extract(self, file_path: Path) -> ExtractionResult:
        errors: list[str] = []
        try:
            # Detect encoding
            raw = file_path.read_bytes()
            for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
                try:
                    text = raw.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                text = raw.decode("utf-8", errors="replace")

            reader = csv.reader(io.StringIO(text))
            rows = [row for row in reader]

            if not rows:
                return ExtractionResult(
                    pages=(ExtractedPage(page_number=1, text=""),),
                    total_pages=1,
                    extraction_method="csv_parse",
                )

            # Build a text representation for embedding
            header = rows[0] if rows else []
            text_lines = [", ".join(header)]
            for row in rows[1:]:
                record = ", ".join(
                    f"{h}: {v}" for h, v in zip(header, row) if v.strip()
                )
                if record:
                    text_lines.append(record)

            page = ExtractedPage(
                page_number=1,
                text="\n".join(text_lines),
                tables=(rows,),
                metadata={
                    "row_count": len(rows) - 1,  # exclude header
                    "column_count": len(header),
                    "columns": header,
                },
            )

            return ExtractionResult(
                pages=(page,),
                total_pages=1,
                extraction_method="csv_parse",
                metadata={"row_count": len(rows) - 1, "columns": header},
            )

        except Exception as e:
            errors.append(str(e))
            return ExtractionResult(
                pages=(),
                total_pages=0,
                extraction_method="csv_parse",
                errors=tuple(errors),
            )
