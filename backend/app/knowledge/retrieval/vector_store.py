"""Vector store for semantic search.

Provides an interface and in-memory implementation for storing
and searching document chunks by vector similarity.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.domain.industrial.document import DocumentChunk

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SearchResult:
    """A semantic search result with similarity score."""
    chunk: DocumentChunk
    similarity_score: float


class VectorStore(ABC):
    """Abstract interface for a vector store."""

    @abstractmethod
    def add_chunks(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> None:
        """Add chunks and their embeddings to the store."""
        ...

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """Search for the most similar chunks."""
        ...


class InMemoryVectorStore(VectorStore):
    """Simple in-memory vector store using cosine similarity.

    Suitable for hackathon demonstrations and local testing
    without external database dependencies (like ChromaDB or Pinecone).
    """

    def __init__(self) -> None:
        self._chunks: list[DocumentChunk] = []
        self._embeddings: list[list[float]] = []

    def add_chunks(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks and embeddings must match.")

        self._chunks.extend(chunks)
        self._embeddings.extend(embeddings)
        logger.info(f"Added {len(chunks)} chunks to vector store. Total: {len(self._chunks)}")

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        if not self._chunks:
            return []

        # Simple cosine similarity (assuming normalized vectors)
        results: list[SearchResult] = []
        for chunk, emb in zip(self._chunks, self._embeddings):
            # Apply metadata filters if provided
            if filters and not self._matches_filters(chunk, filters):
                continue

            score = self._cosine_similarity(query_embedding, emb)
            results.append(SearchResult(chunk=chunk, similarity_score=score))

        # Sort by score descending
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_k]

    def _cosine_similarity(self, v1: list[float], v2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm1 = sum(a * a for a in v1) ** 0.5
        norm2 = sum(b * b for b in v2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

    def _matches_filters(self, chunk: DocumentChunk, filters: dict[str, Any]) -> bool:
        """Check if a chunk matches the metadata filters."""
        if not chunk.provenance:
            return False

        # Filter by document type
        if "document_type" in filters:
            if chunk.provenance.document_type != filters["document_type"]:
                return False

        # Filter by document ID
        if "document_id" in filters:
            if chunk.provenance.document_id != filters["document_id"]:
                return False

        return True
