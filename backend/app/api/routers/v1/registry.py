"""
Algorithms and Projections REST API.

Exposes the Algorithm Registry and Projection Registry to the Developer Console.
"""
from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

class GenericObjectDTO(BaseModel, extra='allow'):
    pass

from app.core.algorithms.registry import get_algorithm_registry
from app.core.projections.registry import get_projection_registry
from app.core.events.store import get_event_store

router = APIRouter(prefix="/api/v1/registry", tags=["Registries"])


# ─────────────────────────────────────────────────────────
# Algorithm endpoints
# ─────────────────────────────────────────────────────────

@router.get("/algorithms", response_model=GenericObjectDTO)
async def list_algorithms():
    registry = get_algorithm_registry()
    return {
        "algorithms": [
            {
                "algorithm_id": a.algorithm_id,
                "name": a.name,
                "version": a.version,
                "description": a.description,
                "formula": a.formula,
                "inputs": [{"name": i.name, "type": i.type, "description": i.description, "required": i.required} for i in a.inputs],
                "outputs": [{"name": o.name, "type": o.type, "description": o.description} for o in a.outputs],
                "normalization": a.normalization,
                "thresholds": a.thresholds,
                "consumers": a.consumers,
                "tags": a.tags,
                "deprecated": a.deprecated,
                "superseded_by": a.superseded_by,
                "registered_at": a.registered_at,
                "diagnostics": {
                    "avg_latency_ms": a.avg_latency_ms,
                    "avg_memory_mb": a.avg_memory_mb,
                    "execution_count": a.execution_count,
                    "failure_count": a.failure_count,
                }
            }
            for a in registry.list_all()
        ]
    }


@router.get("/algorithms/{algorithm_id}", response_model=GenericObjectDTO)
async def get_algorithm(algorithm_id: str):
    registry = get_algorithm_registry()
    a = registry.get(algorithm_id)
    if not a:
        raise HTTPException(404, detail=f"Algorithm '{algorithm_id}' not found")
    return {
        "algorithm_id": a.algorithm_id,
        "name": a.name,
        "version": a.version,
        "description": a.description,
        "formula": a.formula,
        "inputs": [{"name": i.name, "type": i.type, "description": i.description, "required": i.required, "example": i.example} for i in a.inputs],
        "outputs": [{"name": o.name, "type": o.type, "description": o.description, "unit": o.unit} for o in a.outputs],
        "normalization": a.normalization,
        "confidence_range": a.confidence_range,
        "thresholds": a.thresholds,
        "consumers": a.consumers,
        "benchmarks": [
            {"dataset_id": b.dataset_id, "accuracy": b.accuracy, "f1": b.f1, "evaluated_at": b.evaluated_at}
            for b in a.benchmarks
        ],
        "tags": a.tags,
        "deprecated": a.deprecated,
        "superseded_by": a.superseded_by,
        "diagnostics": {
            "avg_latency_ms": a.avg_latency_ms,
            "avg_memory_mb": a.avg_memory_mb,
            "execution_count": a.execution_count,
            "failure_count": a.failure_count,
        }
    }


# ─────────────────────────────────────────────────────────
# Projection endpoints
# ─────────────────────────────────────────────────────────

@router.get("/projections", response_model=GenericObjectDTO)
async def list_projections():
    """Projection Status page: all projections with health, counts, and last-built time."""
    registry = get_projection_registry()
    return {
        "projections": [
            {
                "projection_id": p.projection_id,
                "name": p.name,
                "version": p.version,
                "description": p.description,
                "depends_on": p.depends_on,
                "rebuild_triggers": p.rebuild_triggers,
                "upstream_projections": p.upstream_projections,
                "tags": p.tags,
                "status": p.status,
                "last_built_at": p.last_built_at,
                "last_build_duration_ms": p.last_build_duration_ms,
                "node_count": p.node_count,
                "edge_count": p.edge_count,
                "record_count": p.record_count,
                "last_error": p.last_error,
            }
            for p in registry.list_all()
        ]
    }


@router.get("/projections/{projection_id}", response_model=GenericObjectDTO)
async def get_projection(projection_id: str):
    registry = get_projection_registry()
    p = registry.get(projection_id)
    if not p:
        raise HTTPException(404, detail=f"Projection '{projection_id}' not found")
    return {
        "projection_id": p.projection_id,
        "name": p.name,
        "version": p.version,
        "description": p.description,
        "depends_on": p.depends_on,
        "rebuild_triggers": p.rebuild_triggers,
        "upstream_projections": p.upstream_projections,
        "tags": p.tags,
        "status": p.status,
        "last_built_at": p.last_built_at,
        "last_build_duration_ms": p.last_build_duration_ms,
        "node_count": p.node_count,
        "edge_count": p.edge_count,
        "record_count": p.record_count,
        "last_error": p.last_error,
    }


@router.get("/projections/{projection_id}/analytics", response_model=GenericObjectDTO)
async def get_projection_analytics(projection_id: str):
    """Projection Dependency Explorer: return DAG of dependencies for visual rendering."""
    registry = get_projection_registry()
    p = registry.get(projection_id)
    if not p:
        raise HTTPException(404, detail=f"Projection '{projection_id}' not found")
    return {"projection_id": projection_id, "analytics": p.get_analytics()}


@router.get("/projections/{projection_id}/dependency-graph")
async def get_projection_dependency_graph(projection_id: str):
    """Projection Dependency Explorer: return DAG of dependencies for visual rendering."""
    registry = get_projection_registry()
    p = registry.get(projection_id)
    if not p:
        raise HTTPException(404, detail=f"Projection '{projection_id}' not found")

    nodes = [{"id": projection_id, "type": "projection", "label": p.name}]
    edges = []

    for dep in p.depends_on:
        nodes.append({"id": dep, "type": "canonical", "label": dep})
        edges.append({"source": dep, "target": projection_id, "label": "feeds"})

    for upstream in p.upstream_projections:
        up = registry.get(upstream)
        nodes.append({"id": upstream, "type": "projection", "label": up.name if up else upstream})
        edges.append({"source": upstream, "target": projection_id, "label": "depends"})

    return {"nodes": nodes, "edges": edges}


# ─────────────────────────────────────────────────────────
# Event Store endpoints
# ─────────────────────────────────────────────────────────

@router.get("/events")
async def list_events(
    event_type: Optional[str] = None,
    execution_id: Optional[str] = None,
    repository_session_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """Event Explorer: query the immutable event log."""
    store = get_event_store()
    events = store.get_events(
        event_types=[event_type] if event_type else None,
        execution_id=execution_id,
        repository_session_id=repository_session_id,
        limit=limit,
        offset=offset,
    )
    return {
        "events": [
            {
                "event_id": e.event_id,
                "event_type": e.event_type,
                "occurred_at": e.occurred_at,
                "schema_version": e.schema_version,
                "source_component": e.source_component,
                "workspace_id": e.workspace_id,
                "repository_session_id": e.repository_session_id,
                "execution_id": e.execution_id,
                "payload": e.payload,
                "affected_object_ids": e.affected_object_ids,
            }
            for e in events
        ],
        "total": store.count([event_type] if event_type else None),
    }


@router.get("/events/object/{object_id}")
async def get_events_for_object(object_id: str, limit: int = 50):
    """Lineage: all events that touched a specific canonical object."""
    store = get_event_store()
    events = store.get_events_for_object(object_id, limit=limit)
    return {
        "object_id": object_id,
        "events": [
            {
                "event_id": e.event_id,
                "event_type": e.event_type,
                "occurred_at": e.occurred_at,
                "source_component": e.source_component,
                "payload": e.payload,
            }
            for e in events
        ],
    }


# ─────────────────────────────────────────────────────────
# Projection Engine Lifecycle Endpoints
# ─────────────────────────────────────────────────────────

@router.get("/projection-engine/status")
async def get_projection_engine_status():
    """Projection Status page: health, counts, latency, and metrics for all projections."""
    from app.core.projections.engine import get_projection_engine
    engine = get_projection_engine()
    return {"projections": engine.get_status()}


@router.get("/projections/{projection_id}/search", response_model=GenericObjectDTO)
async def search_projection(projection_id: str, q: str):
    """Force a full rebuild of a single projection."""
    from app.core.projections.engine import get_projection_engine
    engine = get_projection_engine()
    result = await engine.search(projection_id, q)
    return {
        "projection_id": projection_id,
        "query": q,
        "results": result
    }


@router.post("/projection-engine/rebuild/{projection_id}")
async def rebuild_projection(projection_id: str):
    """Force a full rebuild of a single projection."""
    from app.core.projections.engine import get_projection_engine
    engine = get_projection_engine()
    result = await engine.rebuild(projection_id)
    return {
        "build_id": result.build_id,
        "projection_id": result.projection_id,
        "success": result.success,
        "duration_ms": result.duration_ms,
        "node_count": result.node_count,
        "record_count": result.record_count,
        "error": result.error,
    }


@router.post("/projection-engine/rebuild-all")
async def rebuild_all_projections():
    """Full rebuild of all projections in dependency order."""
    from app.core.projections.engine import get_projection_engine
    engine = get_projection_engine()
    results = await engine.rebuild_all()
    return {
        "total": len(results),
        "succeeded": sum(1 for r in results if r.success),
        "failed": sum(1 for r in results if not r.success),
        "results": [
            {
                "projection_id": r.projection_id,
                "success": r.success,
                "duration_ms": r.duration_ms,
                "record_count": r.record_count,
                "error": r.error,
            }
            for r in results
        ],
    }


@router.post("/projection-engine/invalidate/{projection_id}")
async def invalidate_projection(projection_id: str):
    """Mark a projection stale without rebuilding it."""
    from app.core.projections.engine import get_projection_engine
    engine = get_projection_engine()
    await engine.invalidate(projection_id)
    return {"projection_id": projection_id, "status": "stale"}


@router.get("/projections/{projection_id}/visualize", response_model=GenericObjectDTO)
async def visualize_projection(projection_id: str, focus_node_id: Optional[str] = None, depth: int = 1):
    """Replay from event log and rebuild all affected projections."""
    from app.core.projections.engine import get_projection_engine
    engine = get_projection_engine()
    return engine.get_visualization(projection_id, focus_node_id, depth)


@router.post("/projection-engine/replay")
async def replay_projections(since: Optional[str] = None, until: Optional[str] = None):
    """Replay from event log and rebuild all affected projections."""
    from app.core.projections.engine import get_projection_engine
    engine = get_projection_engine()
    results = await engine.replay(since=since, until=until)
    return {
        "total": len(results),
        "succeeded": sum(1 for r in results if r.success),
        "results": [{"projection_id": r.projection_id, "success": r.success, "duration_ms": r.duration_ms} for r in results],
    }


@router.get("/projection-engine/history/{projection_id}")
async def get_projection_history(projection_id: str, limit: int = 20):
    """Projection execution history — every build attempt with metrics."""
    from app.core.projections.engine import get_projection_engine
    engine = get_projection_engine()
    history = engine.get_execution_history(projection_id, limit=limit)
    return {"projection_id": projection_id, "history": history}


@router.get("/projections/{projection_id}/nodes", response_model=GenericObjectDTO)
async def get_projection_nodes(projection_id: str, limit: int = 100, offset: int = 0):
    """Projection execution history — every build attempt with metrics."""
    from app.core.projections.engine import get_projection_engine
    engine = get_projection_engine()
    return engine.get_nodes(projection_id, limit=limit, offset=offset)


@router.get("/projection-engine/impact/{object_type}")
async def simulate_impact(object_type: str):
    """
    Projection Dependency Explorer: show what projections would rebuild
    if a canonical object of the given type changed.
    Example: /api/v1/registry/projection-engine/impact/measurement
    """
    from app.core.projections.engine import get_projection_engine
    engine = get_projection_engine()
    return engine.simulate_impact(object_type)
