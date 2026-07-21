"""Base adapter protocol for document ingestion.

All document adapters implement this protocol so the
ingestion pipeline can handle any document format uniformly.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ExtractedPage:
    """A single page (or logical section) of extracted content."""
    page_number: int
    text: str
    tables: tuple[list[list[str]], ...] = ()    # list of tables, each table is rows x cols
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExtractionResult:
    """Result of extracting content from a document."""
    pages: tuple[ExtractedPage, ...]
    total_pages: int = 0
    extraction_method: str = "text_extraction"
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: tuple[str, ...] = ()


class DocumentAdapter(ABC):
    """Abstract adapter for extracting content from a document."""

    @abstractmethod
    def can_handle(self, file_path: Path) -> bool:
        """Check if this adapter can handle the given file."""
        ...

    @abstractmethod
    def extract(self, file_path: Path) -> ExtractionResult:
        """Extract text and tables from the document."""
        ...

    @property
    @abstractmethod
    def supported_extensions(self) -> tuple[str, ...]:
        """File extensions this adapter supports."""
        ...
