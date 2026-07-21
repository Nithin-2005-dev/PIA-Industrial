"""Semantic chunking engine.

Splits extracted document content into semantically meaningful
chunks for embedding and retrieval. Supports:
- Section-aware chunking (respects headings)
- Fixed-size chunking with overlap
- Table-aware chunking (tables stay intact)
- Provenance preservation (each chunk knows its source)
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from app.domain.industrial.document import DocumentChunk, DocumentProvenance
from app.ingestion.adapters.base import ExtractedPage


@dataclass(frozen=True)
class ChunkingConfig:
    """Configuration for the chunking engine."""
    max_chunk_size: int = 1000                  # characters
    chunk_overlap: int = 200                    # overlap between chunks
    min_chunk_size: int = 50                    # skip very short chunks
    section_separators: tuple[str, ...] = (
        r"\n#{1,6}\s",                          # markdown headings
        r"\n[A-Z][A-Z\s]+\n",                  # ALL CAPS section headers
        r"\n\d+\.\s",                           # numbered sections
        r"\n-{3,}",                             # horizontal rules
        r"\n={3,}",                             # double horizontal rules
    )
    preserve_tables: bool = True


class ChunkingEngine:
    """Splits document content into chunks with provenance."""

    def __init__(self, config: ChunkingConfig | None = None):
        self._config = config or ChunkingConfig()

    def chunk_pages(
        self,
        pages: tuple[ExtractedPage, ...],
        document_id: str,
        document_name: str,
        document_type: str,
    ) -> list[DocumentChunk]:
        """Chunk all pages of a document.

        Returns a list of DocumentChunks with full provenance.
        """
        all_chunks: list[DocumentChunk] = []
        chunk_index = 0

        for page in pages:
            # Handle tables as separate chunks (if configured)
            if self._config.preserve_tables and page.tables:
                for table_idx, table in enumerate(page.tables):
                    table_text = self._table_to_text(table)
                    if len(table_text.strip()) >= self._config.min_chunk_size:
                        chunk_id = f"{document_id}:p{page.page_number}:t{table_idx}"
                        all_chunks.append(DocumentChunk(
                            chunk_id=chunk_id,
                            document_id=document_id,
                            content=table_text,
                            page_number=page.page_number,
                            section=f"Table {table_idx + 1}",
                            chunk_index=chunk_index,
                            token_count=len(table_text.split()),
                            provenance=DocumentProvenance(
                                document_id=document_id,
                                document_name=document_name,
                                document_type=document_type,
                                page_number=page.page_number,
                                section=f"Table {table_idx + 1}",
                                chunk_id=chunk_id,
                                source_text=table_text[:200],
                                extraction_method="table_parse",
                            ),
                        ))
                        chunk_index += 1

            # Chunk the page text
            if page.text.strip():
                text_chunks = self._split_text(page.text)
                for text in text_chunks:
                    if len(text.strip()) < self._config.min_chunk_size:
                        continue

                    chunk_id = f"{document_id}:p{page.page_number}:c{chunk_index}"
                    section = self._detect_section(text)

                    all_chunks.append(DocumentChunk(
                        chunk_id=chunk_id,
                        document_id=document_id,
                        content=text,
                        page_number=page.page_number,
                        section=section,
                        chunk_index=chunk_index,
                        token_count=len(text.split()),
                        provenance=DocumentProvenance(
                            document_id=document_id,
                            document_name=document_name,
                            document_type=document_type,
                            page_number=page.page_number,
                            section=section,
                            chunk_id=chunk_id,
                            source_text=text[:200],
                            extraction_method="text_extraction",
                        ),
                    ))
                    chunk_index += 1

        return all_chunks

    def _split_text(self, text: str) -> list[str]:
        """Split text into chunks using section-aware splitting.

        1. Try to split on section boundaries
        2. If sections are too large, split on paragraph boundaries
        3. If paragraphs are too large, split on sentence boundaries
        4. Fall back to fixed-size splitting
        """
        max_size = self._config.max_chunk_size
        overlap = self._config.chunk_overlap

        # First try section-based splitting
        sections = self._split_on_sections(text)

        chunks: list[str] = []
        for section in sections:
            if len(section) <= max_size:
                chunks.append(section)
            else:
                # Section too large — split on paragraphs
                paragraphs = section.split("\n\n")
                current = ""
                for para in paragraphs:
                    if len(current) + len(para) + 2 <= max_size:
                        current = current + "\n\n" + para if current else para
                    else:
                        if current:
                            chunks.append(current)
                        if len(para) <= max_size:
                            current = para
                        else:
                            # Paragraph too large — fixed-size split
                            chunks.extend(self._fixed_split(para, max_size, overlap))
                            current = ""
                if current:
                    chunks.append(current)

        # Apply overlap between adjacent chunks
        if overlap > 0 and len(chunks) > 1:
            overlapped = [chunks[0]]
            for i in range(1, len(chunks)):
                prev_tail = chunks[i - 1][-overlap:]
                overlapped.append(prev_tail + "\n" + chunks[i])
            return overlapped

        return chunks

    def _split_on_sections(self, text: str) -> list[str]:
        """Split text on section headings."""
        combined_pattern = "|".join(self._config.section_separators)
        parts = re.split(combined_pattern, text)
        return [p.strip() for p in parts if p.strip()]

    def _fixed_split(
        self,
        text: str,
        max_size: int,
        overlap: int,
    ) -> list[str]:
        """Fixed-size splitting with overlap."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + max_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        return chunks

    def _detect_section(self, text: str) -> str | None:
        """Try to detect a section heading in the chunk."""
        lines = text.strip().split("\n")
        if not lines:
            return None

        first_line = lines[0].strip()

        # Markdown heading
        if first_line.startswith("#"):
            return first_line.lstrip("# ").strip()

        # All-caps heading
        if first_line.isupper() and len(first_line) < 100:
            return first_line

        # Numbered heading (e.g., "4.2 Maintenance Procedures")
        match = re.match(r"^(\d+\.?\d*\.?\d*)\s+(.+)", first_line)
        if match:
            return first_line

        return None

    def _table_to_text(self, table: list[list[str]]) -> str:
        """Convert a table to a readable text representation."""
        if not table:
            return ""

        lines: list[str] = []
        header = table[0]
        lines.append(" | ".join(str(cell) for cell in header))
        lines.append("-" * len(lines[0]))

        for row in table[1:]:
            # Create a record-style representation
            record_parts = []
            for h, v in zip(header, row):
                if v and str(v).strip():
                    record_parts.append(f"{h}: {v}")
            if record_parts:
                lines.append(", ".join(record_parts))

        return "\n".join(lines)
