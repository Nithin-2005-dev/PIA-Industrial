"""
PIA Projection Registry.

Projections are versioned, incrementally-maintained read models derived from the Operational Store.
They are NOT the canonical source of truth — they are query-optimized views.

Every projection declares:
  - dependencies: which canonical record types it reads from
  - rebuild_triggers: which EventTypes should trigger an incremental update
  - version: semantic version of the projection schema
  - schema: the shape of the output objects

Adding a new projection requires ONLY registering it here.
The ProjectionEngine queries the registry to know what to build and when.
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type

from app.core.events.store import EventType


@dataclass
class ProjectionDefinition:
    """
    A registered projection definition.
    The ProjectionEngine uses this to know how and when to rebuild.
    """
    projection_id: str
    name: str
    version: str
    description: str

    # Which canonical record types this projection reads
    depends_on: List[str] = field(default_factory=list)

    # Which event types should trigger an incremental rebuild
    rebuild_triggers: List[str] = field(default_factory=list)

    # Which projections this one depends on (for ordering)
    upstream_projections: List[str] = field(default_factory=list)

    registered_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat() + "Z")
    tags: List[str] = field(default_factory=list)

    # Runtime state (maintained by ProjectionEngine)
    status: str = "unbuilt"          # unbuilt | building | healthy | stale | failed
    last_built_at: Optional[str] = None
    last_build_duration_ms: float = 0.0
    node_count: int = 0
    edge_count: int = 0
    record_count: int = 0
    last_error: Optional[str] = None
    current_version_id: Optional[str] = None  # unique ID for this built version


class ProjectionRegistry:
    """
    Global registry of all projections in PIA.
    The ProjectionEngine queries this to determine what to build and their dependency order.
    """

    def __init__(self):
        self._projections: Dict[str, ProjectionDefinition] = {}

    def register(self, definition: ProjectionDefinition) -> None:
        if definition.projection_id in self._projections:
            raise ValueError(f"Projection '{definition.projection_id}' already registered.")
        self._projections[definition.projection_id] = definition

    def get(self, projection_id: str) -> Optional[ProjectionDefinition]:
        return self._projections.get(projection_id)

    def list_all(self) -> List[ProjectionDefinition]:
        return list(self._projections.values())

    def get_triggered_by(self, event_type: str) -> List[ProjectionDefinition]:
        """Return all projections that should rebuild when a given event type occurs."""
        return [p for p in self._projections.values() if event_type in p.rebuild_triggers]

    def update_status(self, projection_id: str, status: str,
                      duration_ms: float = 0.0, error: Optional[str] = None,
                      node_count: int = 0, edge_count: int = 0, record_count: int = 0) -> None:
        p = self._projections.get(projection_id)
        if p is None:
            return
        p.status = status
        if status in ("healthy",):
            p.last_built_at = datetime.datetime.utcnow().isoformat() + "Z"
            p.last_build_duration_ms = duration_ms
            p.node_count = node_count
            p.edge_count = edge_count
            p.record_count = record_count
            p.last_error = None
        elif status == "failed":
            p.last_error = error

    def get_dependency_order(self) -> List[ProjectionDefinition]:
        """Return projections in topological order (upstream first)."""
        visited = set()
        order = []

        def visit(pid: str):
            if pid in visited:
                return
            visited.add(pid)
            p = self._projections.get(pid)
            if p is None:
                return
            for upstream in p.upstream_projections:
                visit(upstream)
            order.append(p)

        for pid in self._projections:
            visit(pid)
        return order


# ─────────────────────────────────────────────────────────
# Module-level singleton + built-in projection registrations
# ─────────────────────────────────────────────────────────

_registry = ProjectionRegistry()


def get_projection_registry() -> ProjectionRegistry:
    return _registry


def _register_builtin_projections() -> None:
    projections = [
        ProjectionDefinition(
            projection_id="knowledge_graph_v1",
            name="KnowledgeGraphProjection",
            version="1.0",
            description="Graph of repository entities (developers, files, modules) and their ownership/expertise relationships.",
            depends_on=["measurement", "evidence", "developer", "file", "repositorysession"],
            rebuild_triggers=[
                EventType.MEASUREMENT_CREATED.value,
                EventType.EVIDENCE_CREATED.value,
                EventType.COMMIT_INGESTED.value,
                EventType.SYNC_COMPLETED.value,
            ],
            tags=["graph", "knowledge", "ownership"],
        ),
        ProjectionDefinition(
            projection_id="ownership_v1",
            name="OwnershipProjection",
            version="1.0",
            description="Per-file and per-module ownership distribution across developers.",
            depends_on=["measurement", "developer", "file"],
            rebuild_triggers=[
                EventType.MEASUREMENT_CREATED.value,
                EventType.COMMIT_INGESTED.value,
            ],
            tags=["ownership"],
        ),
        ProjectionDefinition(
            projection_id="risk_v1",
            name="RiskProjection",
            version="1.0",
            description="Bus factor, transfer risk, and knowledge concentration scores per module.",
            depends_on=["measurement", "evidence"],
            upstream_projections=["ownership_v1"],
            rebuild_triggers=[
                EventType.MEASUREMENT_CREATED.value,
                EventType.EVIDENCE_CREATED.value,
            ],
            tags=["risk", "bus_factor"],
        ),
        ProjectionDefinition(
            projection_id="reasoning_graph_v1",
            name="ReasoningGraphProjection",
            version="1.0",
            description="Graph of evidence → observation → inference → recommendation chains from reasoning executions.",
            depends_on=["reasoning", "evidence", "execution"],
            rebuild_triggers=[
                EventType.REASONING_COMPLETED.value,
                EventType.EXECUTION_COMPLETED.value,
            ],
            tags=["reasoning", "graph"],
        ),
        ProjectionDefinition(
            projection_id="benchmark_v1",
            name="BenchmarkProjection",
            version="1.0",
            description="Per-capability accuracy, latency, and regression history from benchmark runs.",
            depends_on=["execution", "measurement", "reasoning"],
            rebuild_triggers=[
                EventType.EXECUTION_COMPLETED.value,
            ],
            tags=["benchmark"],
        ),
    ]
    for p in projections:
        _registry.register(p)


_register_builtin_projections()
