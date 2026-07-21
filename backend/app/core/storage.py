from __future__ import annotations

from dataclasses import asdict
from dataclasses import is_dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
import json


class StorageSerializer:
    def to_jsonable(
        self,
        value: Any,
    ) -> Any:
        if is_dataclass(value):
            return self.to_jsonable(asdict(value))
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, dict):
            return {
                str(key): self.to_jsonable(item)
                for key, item in value.items()
            }
        if isinstance(value, (list, tuple, set)):
            return [
                self.to_jsonable(item)
                for item in value
            ]
        return value


class JsonlRecordStore:
    def __init__(
        self,
        path: Path | str,
        serializer: StorageSerializer | None = None,
    ):
        self.path = Path(path)
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        self._serializer = serializer or StorageSerializer()

    def append(
        self,
        record_type: str,
        key: str,
        payload: Any,
    ) -> None:
        envelope = {
            "type": record_type,
            "key": key,
            "payload": self._serializer.to_jsonable(payload),
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    envelope,
                    sort_keys=True,
                )
                + "\n"
            )

    def read_all(
        self,
        record_type: str | None = None,
    ) -> tuple[dict[str, Any], ...]:
        if not self.path.exists():
            return ()
        records = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = json.loads(line)
                if record_type is None or record["type"] == record_type:
                    records.append(record)
        return tuple(records)

    def find(
        self,
        record_type: str,
        key: str,
    ) -> dict[str, Any] | None:
        for record in self.read_all(record_type):
            if record["key"] == key:
                return record
        return None


class PlatformStorage:
    def __init__(
        self,
        root: Path | str = "backend/data/platform",
    ):
        self.root = Path(root)
        self.observations = JsonlRecordStore(self.root / "observations.jsonl")
        self.measurements = JsonlRecordStore(self.root / "measurements.jsonl")
        self.evidence = JsonlRecordStore(self.root / "evidence.jsonl")
        self.checkpoints = JsonlRecordStore(self.root / "checkpoints.jsonl")
        self.history = JsonlRecordStore(self.root / "history.jsonl")

    def append_observation(
        self,
        observation,
    ) -> None:
        self.observations.append(
            "observation",
            observation.observation_id,
            observation,
        )

    def append_measurement(
        self,
        measurement,
    ) -> None:
        self.measurements.append(
            "measurement",
            measurement.id,
            measurement,
        )

    def append_evidence(
        self,
        evidence,
    ) -> None:
        self.evidence.append(
            "evidence",
            evidence.evidence_id,
            evidence,
        )

    def save_checkpoint(
        self,
        adapter: str,
        checkpoint,
    ) -> None:
        self.checkpoints.append(
            "checkpoint",
            adapter,
            checkpoint,
        )

    def append_history(
        self,
        key: str,
        snapshot,
    ) -> None:
        self.history.append(
            "history",
            key,
            snapshot,
        )

