"""Duplicate document detection.

Uses SHA-256 file hashing to detect duplicate documents.
Prevents re-processing of already-ingested content.
"""
from __future__ import annotations

import hashlib
from pathlib import Path


class DuplicateDetector:
    """Detects duplicate documents by file hash."""

    def __init__(self) -> None:
        self._known_hashes: dict[str, str] = {}  # hash -> document_id

    def compute_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of a file."""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def is_duplicate(self, file_hash: str) -> bool:
        """Check if a file hash has already been registered."""
        return file_hash in self._known_hashes

    def get_existing_document_id(self, file_hash: str) -> str | None:
        """Get the document ID of an already-registered file."""
        return self._known_hashes.get(file_hash)

    def register(self, file_hash: str, document_id: str) -> None:
        """Register a new file hash."""
        self._known_hashes[file_hash] = document_id

    @property
    def registered_count(self) -> int:
        return len(self._known_hashes)
