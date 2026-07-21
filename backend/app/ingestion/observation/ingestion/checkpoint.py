from __future__ import annotations

from dataclasses import replace

from app.ingestion.observation.ingestion.models import SyncCursor
from app.core.common import utc_now


class CheckpointStore:
    def __init__(
        self,
    ):
        self._checkpoints: dict[str, SyncCursor] = {}

    def get(
        self,
        adapter: str,
    ) -> SyncCursor | None:
        return self._checkpoints.get(adapter)

    def save(
        self,
        cursor: SyncCursor,
    ) -> SyncCursor:
        stamped = replace(
            cursor,
            updated_at=utc_now(),
        )
        self._checkpoints[cursor.adapter] = stamped
        return stamped

    def all(
        self,
    ) -> tuple[SyncCursor, ...]:
        return tuple(self._checkpoints.values())

