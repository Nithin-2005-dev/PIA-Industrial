"""Document registry.

Maintains an in-memory registry of all ingested documents,
their metadata, chunks, and processing status.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from app.domain.industrial.document import (
    Document,
    DocumentChunk,
    DocumentMetadata,
    DocumentStatus,
    DocumentType,
    DocumentFormat,
)


class DocumentRegistry:
    """In-memory registry of ingested documents."""

    def __init__(self) -> None:
        self._documents: dict[str, Document] = {}
        self._chunks: dict[str, list[DocumentChunk]] = {}  # document_id -> chunks

    def register(self, document: Document) -> None:
        """Register a new document."""
        self._documents[document.document_id] = document

    def get(self, document_id: str) -> Document | None:
        """Get a document by ID."""
        return self._documents.get(document_id)

    def update_status(self, document_id: str, status: DocumentStatus) -> None:
        """Update the processing status of a document."""
        doc = self._documents.get(document_id)
        if doc:
            # Rebuild with new status (immutable dataclass)
            self._documents[document_id] = Document(
                document_id=doc.document_id,
                name=doc.name,
                document_type=doc.document_type,
                document_format=doc.document_format,
                file_hash=doc.file_hash,
                file_path=doc.file_path,
                file_size_bytes=doc.file_size_bytes,
                status=status,
                ingested_at=doc.ingested_at,
                doc_metadata=doc.doc_metadata,
                chunks=doc.chunks,
                version=doc.version,
                previous_version_id=doc.previous_version_id,
                metadata=doc.metadata,
            )

    def store_chunks(self, document_id: str, chunks: list[DocumentChunk]) -> None:
        """Store chunks for a document."""
        self._chunks[document_id] = chunks

    def get_chunks(self, document_id: str) -> list[DocumentChunk]:
        """Get all chunks for a document."""
        return self._chunks.get(document_id, [])

    def get_all_chunks(self) -> list[DocumentChunk]:
        """Get all chunks across all documents."""
        all_chunks: list[DocumentChunk] = []
        for chunks in self._chunks.values():
            all_chunks.extend(chunks)
        return all_chunks

    def list_documents(self) -> list[Document]:
        """List all registered documents."""
        return list(self._documents.values())

    def find_by_type(self, doc_type: DocumentType) -> list[Document]:
        """Find documents by type."""
        return [
            doc for doc in self._documents.values()
            if doc.document_type == doc_type
        ]

    def find_by_status(self, status: DocumentStatus) -> list[Document]:
        """Find documents by status."""
        return [
            doc for doc in self._documents.values()
            if doc.status == status
        ]

    @property
    def document_count(self) -> int:
        return len(self._documents)

    @property
    def total_chunk_count(self) -> int:
        return sum(len(chunks) for chunks in self._chunks.values())
