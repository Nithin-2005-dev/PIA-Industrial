from __future__ import annotations
from abc import ABC, abstractmethod
from app.ingestion.observation.domain import Observation
from app.ingestion.observation.ingestion.models import RawObservationRecord


class IDeduplicationCache(ABC):
    """Distributed cache interface for idempotency checks."""
    
    @abstractmethod
    def check_and_set_raw(self, key: tuple[str, str, str]) -> bool:
        """Return True if key already exists, else add it and return False."""

    @abstractmethod
    def check_and_set_observation(self, observation_id: str) -> bool:
        """Return True if observation_id already exists, else add it and return False."""


class LocalMemoryDeduplicationCache(IDeduplicationCache):
    """In-memory deduplication cache for testing (stateful, breaks in multi-pod)."""
    
    def __init__(self):
        self._raw_keys: set[tuple[str, str, str]] = set()
        self._observation_ids: set[str] = set()
        
    def check_and_set_raw(self, key: tuple[str, str, str]) -> bool:
        if key in self._raw_keys:
            return True
        self._raw_keys.add(key)
        return False
        
    def check_and_set_observation(self, observation_id: str) -> bool:
        if observation_id in self._observation_ids:
            return True
        self._observation_ids.add(observation_id)
        return False


class RedisDeduplicationCache(IDeduplicationCache):
    """Redis-backed distributed cache for idempotency in Kubernetes."""
    
    def __init__(self, connection_url: str):
        raise NotImplementedError("Redis cache requires external infrastructure configuration")
        
    def check_and_set_raw(self, key: tuple[str, str, str]) -> bool:
        raise NotImplementedError("Redis cache requires external infrastructure configuration")
        
    def check_and_set_observation(self, observation_id: str) -> bool:
        raise NotImplementedError("Redis cache requires external infrastructure configuration")


class ObservationDeduplicator:
    def __init__(
        self,
        cache: IDeduplicationCache | None = None,
    ):
        self._cache = cache or LocalMemoryDeduplicationCache()

    def is_duplicate_raw(
        self,
        record: RawObservationRecord,
    ) -> bool:
        key = (
            record.source.provider,
            record.record_type,
            record.record_id,
        )
        return self._cache.check_and_set_raw(key)

    def is_duplicate_observation(
        self,
        observation: Observation,
    ) -> bool:
        return self._cache.check_and_set_observation(observation.observation_id)
