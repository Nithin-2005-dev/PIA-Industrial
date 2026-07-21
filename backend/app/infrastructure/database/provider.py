"""
PIA Persistence Provider Abstraction.

The engine never imports SQLAlchemy or SQLite directly.
Everything goes through this PersistenceProvider interface.
Swapping to Postgres or DuckDB requires only a new provider implementation.
"""
from __future__ import annotations

import abc
from typing import Any, Dict, List, Optional, Type, TypeVar

T = TypeVar("T")


class PersistenceProvider(abc.ABC):
    """
    Abstract persistence interface. The engine never knows which database is behind this.
    """

    @abc.abstractmethod
    def initialize(self) -> None:
        """Create all required tables/collections if they don't exist."""

    @abc.abstractmethod
    def insert(self, record: Any) -> Any:
        """Persist a new canonical record. Returns the persisted record with generated ID."""

    @abc.abstractmethod
    def update(self, record: Any) -> Any:
        """Update an existing canonical record."""

    @abc.abstractmethod
    def get_by_id(self, model_type: Type[T], object_id: str) -> Optional[T]:
        """Retrieve a single record by its global identity."""

    @abc.abstractmethod
    def query(self, model_type: Type[T], filters: Optional[Dict[str, Any]] = None,
              limit: int = 100, offset: int = 0) -> List[T]:
        """Query records of a given type with optional filters."""

    @abc.abstractmethod
    def count(self, model_type: Type[T], filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records of a given type."""

    @abc.abstractmethod
    def delete(self, model_type: Type[T], object_id: str) -> bool:
        """Delete a record by ID. Returns True if deleted."""

    @abc.abstractmethod
    def search(self, query: str, model_types: Optional[List[Type]] = None,
               limit: int = 50) -> List[Any]:
        """Universal full-text search across all or specified model types."""

    @abc.abstractmethod
    def transaction(self):
        """Context manager for an atomic transaction. Yields control, commits on success, rolls back on error."""

    @abc.abstractmethod
    def close(self) -> None:
        """Release any held resources (connections, file handles, etc.)."""


class PersistenceError(Exception):
    """Raised when a persistence operation fails."""


class RecordNotFoundError(PersistenceError):
    """Raised when a requested record does not exist."""
