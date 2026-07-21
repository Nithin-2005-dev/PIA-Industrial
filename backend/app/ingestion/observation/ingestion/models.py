from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class IngestionMode(str, Enum):
    INITIAL_IMPORT = "initial_import"
    INCREMENTAL = "incremental"
    REPLAY = "replay"


@dataclass(frozen=True)
class ExternalSource:
    provider: str
    adapter: str
    organization: str | None = None
    repository: str | None = None
    tenant_id: str | None = None


@dataclass(frozen=True)
class RawObservationRecord:
    source: ExternalSource
    record_id: str
    record_type: str
    payload: dict[str, Any]
    observed_at: datetime
    signature: str | None = None
    cursor: str | None = None
    offset: int | None = None


@dataclass(frozen=True)
class SyncCursor:
    adapter: str
    cursor: str | None = None
    offset: int = 0
    updated_at: datetime | None = None


@dataclass(frozen=True)
class SyncRequest:
    source: ExternalSource
    mode: IngestionMode = IngestionMode.INCREMENTAL
    cursor: SyncCursor | None = None
    since: datetime | None = None
    until: datetime | None = None
    batch_size: int = 100
    replay: bool = False


@dataclass(frozen=True)
class SyncResult:
    adapter: str
    raw_count: int
    normalized_count: int
    accepted_count: int
    duplicate_count: int
    failed_count: int
    checkpoint: SyncCursor


@dataclass(frozen=True)
class ReplayQuery:
    repository: str | None = None
    organization: str | None = None
    adapter: str | None = None
    developer: str | None = None
    start: datetime | None = None
    end: datetime | None = None

