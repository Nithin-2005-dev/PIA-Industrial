from __future__ import annotations

from app.ingestion.observation.domain import Observation
from app.ingestion.observation.ingestion.models import RawObservationRecord


class ObservationIngestionStore:
    def __init__(
        self,
    ):
        self._raw: list[RawObservationRecord] = []
        self._normalized: list[Observation] = []
        self._processed_evidence: list[object] = []

    def append_raw(
        self,
        record: RawObservationRecord,
    ) -> None:
        self._raw.append(record)

    def append_normalized(
        self,
        observation: Observation,
    ) -> None:
        self._normalized.append(observation)

    def append_processed_evidence(
        self,
        evidence,
    ) -> None:
        self._processed_evidence.append(evidence)

    def raw(
        self,
    ) -> tuple[RawObservationRecord, ...]:
        return tuple(self._raw)

    def normalized(
        self,
    ) -> tuple[Observation, ...]:
        return tuple(self._normalized)

    def processed_evidence(
        self,
    ) -> tuple[object, ...]:
        return tuple(self._processed_evidence)

