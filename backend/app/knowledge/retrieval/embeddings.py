"""Embedding models for semantic retrieval.

Converts text chunks into dense vector embeddings for semantic
similarity search.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class EmbeddingModel(ABC):
    """Abstract interface for text embedding generation."""

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Generate an embedding for a single text."""
        ...

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""
        ...

    @property
    @abstractmethod
    def dimension(self) -> int:
        """The dimensionality of the produced embeddings."""
        ...


class TFIDFEmbeddingModel(EmbeddingModel):
    """A lightweight, zero-dependency embedding model.

    Uses a simple character-trigram hash trick to create
    pseudo-dense embeddings. This is purely for local testing and
    hackathon demonstrations where external ML dependencies
    (like sentence-transformers) are unavailable or too slow.

    Do not use this for actual semantic search in production.
    """

    def __init__(self, dim: int = 256) -> None:
        self._dim = dim

    def embed_text(self, text: str) -> list[float]:
        """Convert text to a normalized hash-frequency vector."""
        vec = [0.0] * self._dim
        text = text.lower()
        if len(text) < 3:
            return vec

        # Simple trigram hashing
        for i in range(len(text) - 2):
            trigram = text[i:i + 3]
            idx = hash(trigram) % self._dim
            vec[idx] += 1.0

        # L2 normalize
        magnitude = sum(x * x for x in vec) ** 0.5
        if magnitude > 0:
            vec = [x / magnitude for x in vec]

        return vec

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(t) for t in texts]

    @property
    def dimension(self) -> int:
        return self._dim


class SentenceTransformerModel(EmbeddingModel):
    """Embedding model using sentence-transformers (HuggingFace).

    Requires `sentence-transformers` package.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(model_name)
        except ImportError:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Run `pip install sentence-transformers`."
            )

    def embed_text(self, text: str) -> list[float]:
        return self._model.encode(text).tolist()  # type: ignore

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts).tolist()  # type: ignore

    @property
    def dimension(self) -> int:
        return self._model.get_sentence_embedding_dimension()  # type: ignore


def get_default_embedding_model() -> EmbeddingModel:
    """Get the best available embedding model."""
    try:
        return SentenceTransformerModel()
    except ImportError:
        logger.warning("sentence-transformers not found. Falling back to TFIDFEmbeddingModel.")
        return TFIDFEmbeddingModel()
