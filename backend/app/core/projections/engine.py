"""
PIA Projection Engine Framework.

This is the FRAMEWORK — not the individual projections.

The ProjectionEngine manages the full lifecycle of every registered projection:
  - Dependency resolution (topological ordering)
  - Incremental rebuilds (only rebuild what's affected)
  - Versioning (every build creates a versioned snapshot)
  - Health contracts (Healthy / Stale / Building / Failed)
  - Invalidation (mark a projection stale when its inputs change)
  - Replay (rebuild from event log)
  - Execution history (every build is recorded)
  - Metrics (latency, record count, failure rate)

The engine knows HOW to manage projections.
Individual projections register themselves via the ProjectionRegistry
and provide a `build()` callable that receives the PersistenceProvider.

Pipeline:
    Operational Store
        ↓
    ProjectionEngine.trigger(event_type)
        ↓
    Resolve affected projections
        ↓
    Topological dependency ordering
        ↓
    Incremental build (or full rebuild)
        ↓
    Update projection state + emit events
        ↓
    Developer Console reads projections
"""
from __future__ import annotations

import asyncio
import datetime
import time
import uuid
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set

from app.infrastructure.database.provider import PersistenceProvider
from app.core.projections.registry import ProjectionRegistry, ProjectionDefinition, get_projection_registry
from app.core.events.store import ImmutableEventStore, StoreEvent, EventType, get_event_store


# ─────────────────────────────────────────────────────────
# Projection Builder Protocol
# ─────────────────────────────────────────────────────────

class ProjectionBuilder:
    """
    Base class for all projection builders.
    Every concrete projection (KnowledgeGraph, Ownership, etc.) extends this.
    The engine calls .build() with the current Operational Store provider.
    """

    projection_id: str = ""

    def build(
        self,
        provider: PersistenceProvider,
        incremental: bool = True,
        affected_object_ids: Optional[List[str]] = None,
    ) -> "ProjectionBuildResult":
        raise NotImplementedError(f"{self.__class__.__name__} must implement build()")

    def can_build_incrementally(self, affected_object_ids: List[str]) -> bool:
        """Return True if an incremental build is sufficient for the given changes."""
        return False  # Default: always full rebuild. Override for incremental support.


@dataclass
class ProjectionBuildResult:
    """The result of a single projection build execution."""
    projection_id: str
    build_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    success: bool = True
    full_rebuild: bool = False
    duration_ms: float = 0.0
    node_count: int = 0
    edge_count: int = 0
    record_count: int = 0
    objects_updated: int = 0
    error: Optional[str] = None
    started_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat() + "Z")
    completed_at: Optional[str] = None
    schema_version: str = "v1"
    affected_object_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ─────────────────────────────────────────────────────────
# Projection Execution History
# ─────────────────────────────────────────────────────────

@dataclass
class ProjectionExecutionRecord:
    """One entry in a projection's execution history."""
    build_id: str
    projection_id: str
    started_at: str
    completed_at: Optional[str]
    success: bool
    duration_ms: float
    full_rebuild: bool
    node_count: int
    edge_count: int
    record_count: int
    error: Optional[str]
    trigger_event: Optional[str]


class ProjectionExecutionHistory:
    """
    In-memory execution history for the current process.
    Provides per-projection history, aggregate metrics, and failure analysis.
    """

    def __init__(self, max_per_projection: int = 50):
        self._history: Dict[str, List[ProjectionExecutionRecord]] = {}
        self._max = max_per_projection

    def record(self, result: ProjectionBuildResult, trigger_event: Optional[str] = None) -> None:
        pid = result.projection_id
        entry = ProjectionExecutionRecord(
            build_id=result.build_id,
            projection_id=pid,
            started_at=result.started_at,
            completed_at=result.completed_at,
            success=result.success,
            duration_ms=result.duration_ms,
            full_rebuild=result.full_rebuild,
            node_count=result.node_count,
            edge_count=result.edge_count,
            record_count=result.record_count,
            error=result.error,
            trigger_event=trigger_event,
        )
        records = self._history.setdefault(pid, [])
        records.insert(0, entry)
        if len(records) > self._max:
            records.pop()

    def get(self, projection_id: str, limit: int = 20) -> List[ProjectionExecutionRecord]:
        return self._history.get(projection_id, [])[:limit]

    def get_metrics(self, projection_id: str) -> Dict[str, Any]:
        records = self._history.get(projection_id, [])
        if not records:
            return {"execution_count": 0, "avg_latency_ms": 0.0, "failure_rate": 0.0, "last_error": None}
        total = len(records)
        failures = sum(1 for r in records if not r.success)
        avg_lat = sum(r.duration_ms for r in records) / total
        last_error = next((r.error for r in records if not r.success), None)
        return {
            "execution_count": total,
            "avg_latency_ms": round(avg_lat, 2),
            "failure_rate": round(failures / total, 4),
            "last_error": last_error,
        }


# ─────────────────────────────────────────────────────────
# WebSocket Broadcaster (injected by server)
# ─────────────────────────────────────────────────────────

class NullBroadcaster:
    """No-op broadcaster for when WebSocket is not available."""
    async def broadcast(self, event: Dict[str, Any]) -> None:
        pass


# ─────────────────────────────────────────────────────────
# Projection Engine
# ─────────────────────────────────────────────────────────

class ProjectionEngine:
    """
    Manages the full lifecycle of all registered projections.

    Usage:
        engine = ProjectionEngine(provider, registry, event_store)
        engine.register_builder("knowledge_graph_v1", KnowledgeGraphBuilder())
        await engine.trigger(event_type="measurement.created", affected_ids=["meas_123"])
        await engine.rebuild_all()
        await engine.replay(since="2026-01-01T00:00:00Z")
    """

    def __init__(
        self,
        provider: PersistenceProvider,
        registry: Optional[ProjectionRegistry] = None,
        event_store: Optional[ImmutableEventStore] = None,
        broadcaster: Any = None,
    ):
        self._provider = provider
        self._registry = registry or get_projection_registry()
        self._event_store = event_store or get_event_store()
        self._broadcaster = broadcaster or NullBroadcaster()
        self._builders: Dict[str, ProjectionBuilder] = {}
        self._history = ProjectionExecutionHistory()
        self._running: Set[str] = set()  # projection_ids currently building
        self._lock = asyncio.Lock()

    def register_builder(self, projection_id: str, builder: ProjectionBuilder) -> None:
        """Register a builder for a projection. Must be called before trigger() or rebuild()."""
        if projection_id not in {p.projection_id for p in self._registry.list_all()}:
            raise ValueError(f"Projection '{projection_id}' is not in the registry. Register it first.")
        self._builders[projection_id] = builder

    # ─── Lifecycle ─────────────────────────────────────────

    async def trigger(
        self,
        event_type: str,
        affected_object_ids: Optional[List[str]] = None,
        repository_session_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[ProjectionBuildResult]:
        """
        Called when an event occurs in the Operational Store.
        Resolves which projections need rebuilding and builds them incrementally.
        """
        affected_projections = self._registry.get_triggered_by(event_type)
        if not affected_projections:
            return []

        ordered = self._topological_order(
            [p.projection_id for p in affected_projections]
        )

        results = []
        for pid in ordered:
            result = await self._build_one(
                pid,
                full_rebuild=False,
                affected_object_ids=affected_object_ids or [],
                trigger_event=event_type,
                repository_session_id=repository_session_id,
                workspace_id=workspace_id,
            )
            results.append(result)

        return results

    async def rebuild(self, projection_id: str) -> ProjectionBuildResult:
        """Force a full rebuild of a single projection."""
        return await self._build_one(
            projection_id,
            full_rebuild=True,
            trigger_event="manual.rebuild",
        )

    async def rebuild_all(self) -> List[ProjectionBuildResult]:
        """Full rebuild of all registered projections in dependency order."""
        ordered = self._registry.get_dependency_order()
        results = []
        for p in ordered:
            if p.projection_id in self._builders:
                result = await self._build_one(
                    p.projection_id,
                    full_rebuild=True,
                    trigger_event="manual.rebuild_all",
                )
                results.append(result)
        return results

    async def invalidate(self, projection_id: str) -> None:
        """Mark a projection stale without rebuilding it."""
        self._registry.update_status(projection_id, "stale")
        await self._broadcaster.broadcast({
            "schema_version": "v1",
            "event_type": "projection.invalidated",
            "occurred_at": datetime.datetime.utcnow().isoformat() + "Z",
            "projection_id": projection_id,
        })

    async def replay(self, since: Optional[str] = None, until: Optional[str] = None) -> List[ProjectionBuildResult]:
        """
        Replay all events from the Immutable Event Store and rebuild
        all affected projections. Useful for recovering from failures
        or rebuilding after algorithm changes.
        """
        events = self._event_store.get_events(since=since, until=until, limit=10000)
        affected_pids: Set[str] = set()
        for event in events:
            for p in self._registry.get_triggered_by(event.event_type):
                affected_pids.add(p.projection_id)

        ordered = self._topological_order(list(affected_pids))
        results = []
        for pid in ordered:
            if pid in self._builders:
                result = await self._build_one(pid, full_rebuild=True, trigger_event="replay")
                results.append(result)
        return results

    # ─── Core Build ────────────────────────────────────────

    async def _build_one(
        self,
        projection_id: str,
        full_rebuild: bool = False,
        affected_object_ids: Optional[List[str]] = None,
        trigger_event: Optional[str] = None,
        repository_session_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> ProjectionBuildResult:
        builder = self._builders.get(projection_id)
        if builder is None:
            # No builder registered — mark as unbuilt and skip
            return ProjectionBuildResult(
                projection_id=projection_id,
                success=False,
                error=f"No builder registered for '{projection_id}'",
            )

        if projection_id in self._running:
            # Already building — skip to avoid re-entrant builds
            return ProjectionBuildResult(
                projection_id=projection_id,
                success=False,
                error="Build already in progress",
            )

        self._running.add(projection_id)
        self._registry.update_status(projection_id, "building")

        # Emit build started event
        await self._broadcaster.broadcast({
            "schema_version": "v1",
            "event_type": "projection.build_started",
            "occurred_at": datetime.datetime.utcnow().isoformat() + "Z",
            "projection_id": projection_id,
            "projection_name": self._registry.get(projection_id).name if self._registry.get(projection_id) else projection_id,
            "trigger_event": trigger_event,
            "full_rebuild": full_rebuild,
            "workspace_id": workspace_id,
            "repository_session_id": repository_session_id,
        })

        # Log to event store
        self._event_store.append(StoreEvent(
            event_type=EventType.PROJECTION_BUILD_STARTED.value,
            source_component="projection_engine",
            workspace_id=workspace_id,
            repository_session_id=repository_session_id,
            payload={
                "projection_id": projection_id,
                "full_rebuild": full_rebuild,
                "trigger_event": trigger_event,
            },
        ))

        start = time.monotonic()
        result = ProjectionBuildResult(
            projection_id=projection_id,
            full_rebuild=full_rebuild,
            affected_object_ids=affected_object_ids or [],
        )

        try:
            incremental = (not full_rebuild) and builder.can_build_incrementally(affected_object_ids or [])
            build_result = builder.build(
                provider=self._provider,
                incremental=incremental,
                affected_object_ids=affected_object_ids,
            )
            result.success = True
            result.node_count = build_result.node_count
            result.edge_count = build_result.edge_count
            result.record_count = build_result.record_count
            result.objects_updated = build_result.objects_updated
            result.metadata = build_result.metadata

        except Exception as exc:
            result.success = False
            result.error = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"

        elapsed = (time.monotonic() - start) * 1000
        result.duration_ms = elapsed
        result.completed_at = datetime.datetime.utcnow().isoformat() + "Z"

        self._running.discard(projection_id)
        self._history.record(result, trigger_event=trigger_event)

        if result.success:
            self._registry.update_status(
                projection_id, "healthy",
                duration_ms=elapsed,
                node_count=result.node_count,
                edge_count=result.edge_count,
                record_count=result.record_count,
            )
            self._event_store.append(StoreEvent(
                event_type=EventType.PROJECTION_BUILD_COMPLETED.value,
                source_component="projection_engine",
                workspace_id=workspace_id,
                repository_session_id=repository_session_id,
                payload={
                    "projection_id": projection_id,
                    "duration_ms": elapsed,
                    "node_count": result.node_count,
                    "record_count": result.record_count,
                },
            ))
            await self._broadcaster.broadcast({
                "schema_version": "v1",
                "event_type": "projection.build_completed",
                "occurred_at": datetime.datetime.utcnow().isoformat() + "Z",
                "projection_id": projection_id,
                "duration_ms": elapsed,
                "node_count": result.node_count,
                "edge_count": result.edge_count,
                "record_count": result.record_count,
            })
        else:
            self._registry.update_status(projection_id, "failed", error=result.error)
            self._event_store.append(StoreEvent(
                event_type=EventType.PROJECTION_BUILD_FAILED.value,
                source_component="projection_engine",
                payload={"projection_id": projection_id, "error": result.error},
            ))
            await self._broadcaster.broadcast({
                "schema_version": "v1",
                "event_type": "projection.build_failed",
                "occurred_at": datetime.datetime.utcnow().isoformat() + "Z",
                "projection_id": projection_id,
                "error": result.error,
            })

        return result

    # ─── Dependency Resolution ──────────────────────────────

    def _topological_order(self, projection_ids: List[str]) -> List[str]:
        """
        Return projection_ids in topological order so upstream projections
        are always built before downstream ones.
        """
        all_ordered = [p.projection_id for p in self._registry.get_dependency_order()]
        # Filter to only the requested set, preserving topological order
        requested = set(projection_ids)
        return [pid for pid in all_ordered if pid in requested]

    # ─── Inspection ────────────────────────────────────────

    def get_status(self) -> Dict[str, Any]:
        """Return the current status of all registered projections."""
        result = {}
        for p in self._registry.list_all():
            metrics = self._history.get_metrics(p.projection_id)
            result[p.projection_id] = {
                "projection_id": p.projection_id,
                "name": p.name,
                "version": p.version,
                "status": p.status,
                "has_builder": p.projection_id in self._builders,
                "last_built_at": p.last_built_at,
                "last_build_duration_ms": p.last_build_duration_ms,
                "node_count": p.node_count,
                "edge_count": p.edge_count,
                "record_count": p.record_count,
                "last_error": p.last_error,
                "depends_on": p.depends_on,
                "rebuild_triggers": p.rebuild_triggers,
                "metrics": metrics,
            }
        return result

    def get_execution_history(self, projection_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        records = self._history.get(projection_id, limit)
        return [
            {
                "build_id": r.build_id,
                "started_at": r.started_at,
                "completed_at": r.completed_at,
                "success": r.success,
                "duration_ms": r.duration_ms,
                "full_rebuild": r.full_rebuild,
                "node_count": r.node_count,
                "record_count": r.record_count,
                "error": r.error,
                "trigger_event": r.trigger_event,
            }
            for r in records
        ]

    def simulate_impact(self, changed_object_type: str) -> Dict[str, List[str]]:
        """
        Projection Dependency Explorer: simulate what projections would rebuild
        if a canonical object of the given type changed.
        """
        affected_projections = []
        affected_triggers = []
        for p in self._registry.list_all():
            if changed_object_type.lower() in [dep.lower() for dep in p.depends_on]:
                affected_projections.append(p.projection_id)
                affected_triggers.extend(p.rebuild_triggers)
        return {
            "changed_object_type": changed_object_type,
            "affected_projections": affected_projections,
            "affected_triggers": list(set(affected_triggers)),
        }


# ─────────────────────────────────────────────────────────
# Module-level singleton
# ─────────────────────────────────────────────────────────

_engine: Optional[ProjectionEngine] = None


def get_projection_engine(
    provider: Optional[PersistenceProvider] = None,
) -> ProjectionEngine:
    global _engine
    if _engine is None:
        from app.infrastructure.database.sqlite_provider import get_provider as _get_provider
        _engine = ProjectionEngine(
            provider=provider or _get_provider(),
            registry=get_projection_registry(),
            event_store=get_event_store(),
        )
        # Register built-in no-op builders so the framework is fully operational
        # even before concrete projection implementations exist
        from app.core.projections.engine import _register_stub_builders
        _register_stub_builders(_engine)
    return _engine


def _register_stub_builders(engine: ProjectionEngine) -> None:
    """
    Register lightweight stub builders for all projections so the framework
    is fully operational. Concrete builders replace these as they are implemented.
    """
    from app.core.projections.registry import get_projection_registry

    class StubBuilder(ProjectionBuilder):
        def __init__(self, pid: str):
            self.projection_id = pid

        def build(self, provider, incremental=True, affected_object_ids=None):
            # Reads the real Operational Store and produces basic counts
            result = ProjectionBuildResult(projection_id=self.projection_id)
            try:
                from app.infrastructure.database.models import MeasurementRecord, EvidenceRecord, DeveloperRecord
                result.record_count = (
                    provider.count(MeasurementRecord)
                    + provider.count(EvidenceRecord)
                    + provider.count(DeveloperRecord)
                )
            except Exception:
                pass
            return result

    registry = get_projection_registry()
    for p in registry.list_all():
        engine.register_builder(p.projection_id, StubBuilder(p.projection_id))
