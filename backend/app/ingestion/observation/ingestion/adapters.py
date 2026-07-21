from __future__ import annotations

from typing import Type, Dict, Any, Callable
from abc import ABC, abstractmethod
from app.ingestion.observation.ingestion.models import RawObservationRecord
from app.ingestion.observation.ingestion.models import SyncRequest
from app.ingestion.observation.ingestion.models import SyncCursor


class ObservationAdapter(ABC):
    name: str
    provider: str
    supported_record_types: tuple[str, ...]

    @abstractmethod
    def fetch(
        self,
        request: SyncRequest,
    ) -> tuple[RawObservationRecord, SyncCursor]:
        raise NotImplementedError


class AdapterRegistry:
    def __init__(self):
        self._factories: Dict[str, Callable[..., ObservationAdapter]] = {}
        self._active_adapters: Dict[str, ObservationAdapter] = {}

    def register_factory(
        self,
        name: str,
        factory: Callable[..., ObservationAdapter],
    ) -> None:
        self._factories[name] = factory
        
    def instantiate(self, name: str, config: Dict[str, Any]) -> ObservationAdapter:
        if name not in self._factories:
            raise ValueError(f"No factory registered for adapter type '{name}'.")
            
        adapter = self._factories[name](**config)
        
        # Validation Check: Ensure it fulfills the ObservationAdapter protocol natively via ABC
        if not issubclass(type(adapter), ObservationAdapter):
            raise TypeError(f"Adapter '{name}' is broken: Must inherit from ObservationAdapter ABC.")
            
        self._active_adapters[adapter.name] = adapter
        return adapter

    def register(
        self,
        adapter: ObservationAdapter,
    ) -> None:
        """Legacy registration for already-instantiated adapters."""
        self._active_adapters[adapter.name] = adapter

    def get(
        self,
        name: str,
    ) -> ObservationAdapter:
        return self._active_adapters[name]

    def all(
        self,
    ) -> tuple[ObservationAdapter, ...]:
        return tuple(self._active_adapters.values())

    def providers(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    adapter.provider
                    for adapter in self._active_adapters.values()
                }
            )
        )


class StaticObservationAdapter(ObservationAdapter):
    def __init__(
        self,
        name: str,
        provider: str,
        records: tuple[RawObservationRecord, ...] = (),
        supported_record_types: tuple[str, ...] = (),
    ):
        self.name = name
        self.provider = provider
        self._records = records
        self.supported_record_types = supported_record_types

    def fetch(
        self,
        request: SyncRequest,
    ) -> tuple[RawObservationRecord, SyncCursor]:
        offset = (
            request.cursor.offset
            if request.cursor is not None
            else 0
        )
        batch = self._records[
            offset : offset + request.batch_size
        ]
        next_offset = offset + len(batch)
        cursor = (
            batch[-1].cursor
            if batch
            else (
                request.cursor.cursor
                if request.cursor is not None
                else None
            )
        )
        return (
            tuple(batch),
            SyncCursor(
                adapter=self.name,
                cursor=cursor,
                offset=next_offset,
            ),
        )


def default_adapter_names(
) -> tuple[str, ...]:
    return (
        "github",
        "gitlab",
        "bitbucket",
        "jira",
        "linear",
        "azure_devops",
        "slack",
        "teams",
        "email",
        "ci_cd",
        "kubernetes",
        "docker",
        "custom_api",
    )

