"""Snapshot Repository — backend-agnostic persistence for temporal snapshots.

The repository interface is deliberately simple (save / load / retention)
so that future implementations can switch to SQLite, PostgreSQL, object
storage, or another backend without changing the temporal engine.

The default implementation uses one JSON file per snapshot on the local
filesystem.  No code outside this module should depend on filesystem
specifics.
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any

from app.intelligence.temporal.models import SnapshotVersionInfo
from app.intelligence.temporal.models import TemporalSnapshot


def _slugify(text: str) -> str:
    """Convert 'owner/repo' to 'owner_repo' for safe directory names."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", text)


def _snapshot_to_dict(snapshot: TemporalSnapshot) -> dict[str, Any]:
    """Serialize a TemporalSnapshot to a JSON-safe dictionary."""
    data = asdict(snapshot)
    # Convert tuples to lists for JSON (they'll be restored on load)
    return data


def _snapshot_from_dict(data: dict[str, Any]) -> TemporalSnapshot:
    """Deserialize a dictionary back to a TemporalSnapshot."""
    version_info_data = data.pop("version_info", {})
    version_info = SnapshotVersionInfo(**version_info_data)

    # Restore tuple fields from JSON lists
    data["expertise_subjects"] = tuple(data.get("expertise_subjects", ()))
    data["knowledge_topics"] = tuple(data.get("knowledge_topics", ()))
    data["version_info"] = version_info

    return TemporalSnapshot(**data)


class SnapshotRepository:
    """Persists and loads immutable temporal snapshots.

    Storage layout::

        {root}/{repo_slug}/{branch}/v{NNN}.json

    Each file is a self-contained JSON document.  Files are never
    modified after creation — they are append-only and immutable.
    """

    def __init__(
        self,
        root: Path | str,
    ):
        self._root = Path(root)

    def save(
        self,
        snapshot: TemporalSnapshot,
    ) -> Path:
        """Persist a snapshot as an immutable JSON file.

        Returns the path to the written file.
        """
        directory = self._snapshot_dir(snapshot.repository, snapshot.branch)
        directory.mkdir(parents=True, exist_ok=True)

        filename = f"v{snapshot.version:04d}.json"
        path = directory / filename

        data = _snapshot_to_dict(snapshot)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)

        return path

    def load_all(
        self,
        repository: str,
        branch: str,
    ) -> tuple[TemporalSnapshot, ...]:
        """Load all snapshots for a repo/branch pair, sorted by version."""
        directory = self._snapshot_dir(repository, branch)
        if not directory.exists():
            return ()

        snapshots: list[TemporalSnapshot] = []
        for path in sorted(directory.glob("v*.json")):
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            snapshots.append(_snapshot_from_dict(data))

        return tuple(sorted(snapshots, key=lambda s: s.version))

    def load_latest(
        self,
        repository: str,
        branch: str,
    ) -> TemporalSnapshot | None:
        """Load the most recent snapshot, or None if no history exists."""
        all_snapshots = self.load_all(repository, branch)
        if not all_snapshots:
            return None
        return all_snapshots[-1]

    def next_version(
        self,
        repository: str,
        branch: str,
    ) -> int:
        """Return the next version number (1-based)."""
        latest = self.load_latest(repository, branch)
        if latest is None:
            return 1
        return latest.version + 1

    def apply_retention(
        self,
        repository: str,
        branch: str,
        max_snapshots: int = 50,
    ) -> int:
        """Delete oldest snapshots beyond retention limit.

        Returns the number of snapshots deleted.
        """
        directory = self._snapshot_dir(repository, branch)
        if not directory.exists():
            return 0

        files = sorted(directory.glob("v*.json"))
        if len(files) <= max_snapshots:
            return 0

        to_delete = files[: len(files) - max_snapshots]
        for path in to_delete:
            path.unlink()

        return len(to_delete)

    def snapshot_count(
        self,
        repository: str,
        branch: str,
    ) -> int:
        """Return the number of persisted snapshots."""
        directory = self._snapshot_dir(repository, branch)
        if not directory.exists():
            return 0
        return len(list(directory.glob("v*.json")))

    def _snapshot_dir(
        self,
        repository: str,
        branch: str,
    ) -> Path:
        return self._root / _slugify(repository) / _slugify(branch)

    @staticmethod
    def generate_id() -> str:
        """Generate a unique snapshot ID."""
        return str(uuid.uuid4())
