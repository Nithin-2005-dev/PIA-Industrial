from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers.v1 import query, graph, benchmark, datasets, knowledge
from app.api.routers.v1 import store, registry, sync, industrial
from app.api.routers import ws

app = FastAPI(
    title="PIA Developer Console API",
    version="2.0.0",
    description="PIA Platform Observability System — All data served through stable projections and versioned contracts.",
)

# Allow localhost Developer Console
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request
from fastapi.responses import JSONResponse
import logging

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )

# ─────────────────────────────────────────────────────────
# Initialize Operational Store & Event Store at startup
# ─────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    from app.infrastructure.database.sqlite_provider import get_provider
    from app.core.events.store import get_event_store
    from app.core.events.store import StoreEvent, EventType
    from app.core.sync_watcher import get_sync_watcher
    get_provider()  # initializes tables
    event_store = get_event_store()  # initializes event log
    event_store.append(StoreEvent(
        event_type=EventType.SYSTEM_STARTED.value,
        source_component="server",
        payload={"version": "2.0.0"},
    ))
    
    # Start the continuous sync watcher
    watcher = get_sync_watcher()
    watcher.start(interval_seconds=30)

@app.on_event("shutdown")
async def shutdown_event():
    from app.core.sync_watcher import get_sync_watcher
    watcher = get_sync_watcher()
    await watcher.stop()


# ─────────────────────────────────────────────────────────
# Register Routers
# ─────────────────────────────────────────────────────────

# Legacy / existing
app.include_router(query.router)
app.include_router(graph.router)
app.include_router(knowledge.router)
app.include_router(benchmark.router)
app.include_router(datasets.router)

# New Operational Platform
app.include_router(store.router)
app.include_router(registry.router)
app.include_router(sync.router)
app.include_router(industrial.router)

# WebSocket
app.include_router(ws.router)


# ─────────────────────────────────────────────────────────
# Health Contracts
# ─────────────────────────────────────────────────────────

@app.get("/api/health", tags=["Health"])
async def health_check():
    """System Health Contracts — every subsystem reports its status."""
    from app.infrastructure.database.sqlite_provider import get_provider
    from app.core.events.store import get_event_store
    from app.core.projections.registry import get_projection_registry
    from app.core.algorithms.registry import get_algorithm_registry

    try:
        provider = get_provider()
        db_stats = provider.get_table_stats()
        db_status = "healthy"
    except Exception as e:
        db_stats = {}
        db_status = f"error: {e}"

    try:
        event_store = get_event_store()
        event_count = event_store.count()
        event_status = "healthy"
    except Exception as e:
        event_count = 0
        event_status = f"error: {e}"

    proj_registry = get_projection_registry()
    projections = {
        p.projection_id: {
            "status": p.status,
            "last_built_at": p.last_built_at,
            "node_count": p.node_count,
            "record_count": p.record_count,
        }
        for p in proj_registry.list_all()
    }

    algo_registry = get_algorithm_registry()

    return {
        "status": "ok",
        "version": "2.0.0",
        "components": {
            "operational_store": {
                "status": db_status,
                "table_counts": db_stats,
                "total_records": sum(db_stats.values()),
            },
            "event_store": {
                "status": event_status,
                "total_events": event_count,
            },
            "projection_engine": {
                "status": "healthy",
                "projections": projections,
            },
            "algorithm_registry": {
                "status": "healthy",
                "algorithm_count": len(algo_registry.list_all()),
            },
            "cognitive_runtime": {
                "status": "ok",
            },
        },
    }


@app.get("/api/health/industrial", tags=["Health"])
async def industrial_health_check():
    """Industrial runtime health status."""
    try:
        from app.industrial.workspace_runtime import get_industrial_runtime
        runtime = get_industrial_runtime()
        return runtime.health_status()
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

