"""
Operational Store REST API.

All queries go: Database -> Projection -> DTO -> Console.
The console NEVER accesses Python runtime objects directly.
"""
from __future__ import annotations

from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.infrastructure.database.sqlite_provider import get_provider
from app.infrastructure.database.models import (
    WorkspaceRecord, RepositorySessionRecord, CommitRecord,
    DeveloperRecord, FileRecord, MeasurementRecord, EvidenceRecord,
    ExecutionRecord, FactRecord, RuleExecutionRecord, DatasetRecord
)

router = APIRouter(prefix="/api/v1/store", tags=["Operational Store"])


# ─────────────────────────────────────────────────────────
# DTOs (simple — no engine internals exposed)
# ─────────────────────────────────────────────────────────

from typing import Dict, List, Optional, Any

class TableStatsDTO(BaseModel):
    tables: Dict[str, int]
    total_records: int


class ObjectSummaryDTO(BaseModel):
    object_id: str
    object_type: str
    version: int
    created_at: str
    workspace_id: Optional[str]
    execution_id: Optional[str]
    label: str
    metadata: Dict[str, Any] = {}


class SearchResultDTO(BaseModel):
    results: List[ObjectSummaryDTO]
    total: int
    query: str


def _summarize(record) -> ObjectSummaryDTO:
    identity = record.identity
    label = ""
    if hasattr(record, "repository"):
        label = record.repository
    elif hasattr(record, "sha"):
        label = record.sha[:8]
    elif hasattr(record, "email"):
        label = record.email
    elif hasattr(record, "path"):
        label = record.path
    elif hasattr(record, "metric_name"):
        label = f"{record.metric_name}={getattr(record, 'metric_value', ''):.2f}"
    elif hasattr(record, "query"):
        label = record.query[:60]
    elif hasattr(record, "name"):
        label = record.name
    else:
        label = identity.object_id[:12]

    return ObjectSummaryDTO(
        object_id=identity.object_id,
        object_type=identity.object_type,
        version=identity.version,
        created_at=identity.created_at,
        workspace_id=identity.workspace_id,
        execution_id=identity.execution_id,
        label=label,
        metadata=getattr(record, "metadata", {})
    )


# ─────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────

@router.get("/stats", response_model=TableStatsDTO)
async def get_table_stats():
    """Database Inspector: row counts for every canonical table."""
    provider = get_provider()
    stats = provider.get_table_stats()
    return TableStatsDTO(tables=stats, total_records=sum(stats.values()))


@router.get("/search", response_model=SearchResultDTO)
async def search_all(q: str = Query(..., min_length=1), limit: int = 50):
    """Universal Object Explorer: search across all canonical types."""
    provider = get_provider()
    results = provider.search(q, limit=limit)
    summaries = [_summarize(r) for r in results]
    return SearchResultDTO(results=summaries, total=len(summaries), query=q)

class GenericObjectDTO(BaseModel, extra='allow'):
    pass

@router.get("/objects/{object_id}", response_model=GenericObjectDTO)
async def get_object_by_id(object_id: str):
    """Retrieve any engineering object by its UUID."""
    provider = get_provider()
    # In a unified schema, we might not know the type ahead of time, but we can query all known tables
    # or rely on the SQLite provider's search/get functionality. 
    # For now, we search all canonical tables manually:
    from app.infrastructure.database.models import ALL_RECORD_TYPES
    for record_type in ALL_RECORD_TYPES:
        try:
            record = provider.get_by_id(record_type, object_id)
            if record:
                # Convert dataclass to dict
                from dataclasses import asdict
                return GenericObjectDTO(**asdict(record))
        except:
            continue
            
    raise HTTPException(status_code=404, detail="Object not found in any canonical table")


@router.get("/workspaces")
async def list_workspaces(limit: int = 50, offset: int = 0):
    provider = get_provider()
    records = provider.query(WorkspaceRecord, limit=limit, offset=offset)
    return {"items": [_summarize(r) for r in records], "total": provider.count(WorkspaceRecord)}


@router.get("/repositories")
async def list_repository_sessions(workspace_id: Optional[str] = None, limit: int = 50, offset: int = 0):
    provider = get_provider()
    records = provider.query(RepositorySessionRecord, limit=100000, offset=0)
    if workspace_id:
        records = [r for r in records if r.workspace_id == workspace_id or r.identity.workspace_id == workspace_id]

    grouped: Dict[str, List[RepositorySessionRecord]] = {}
    for record in records:
        repo = (record.repository or "").strip().strip("/").lower()
        branch = record.branch or "main"
        if not repo:
            continue
        grouped.setdefault(f"{repo}:{branch}", []).append(record)

    canonical: List[RepositorySessionRecord] = []
    for group in grouped.values():
        group.sort(key=lambda r: r.last_synced_at or r.identity.updated_at or r.identity.created_at, reverse=True)
        primary = group[0]
        primary.metadata = {
            **(primary.metadata or {}),
            "duplicate_session_count": max(0, len(group) - 1),
            "canonical_repository_key": f"{(primary.repository or '').strip().strip('/').lower()}:{primary.branch or 'main'}",
        }
        canonical.append(primary)

    canonical.sort(key=lambda r: r.last_synced_at or r.identity.updated_at or r.identity.created_at, reverse=True)
    page = canonical[offset:offset + limit]
    return {"items": [_summarize(r) for r in page], "total": len(canonical)}


@router.get("/repositories/{session_id}", response_model=GenericObjectDTO)
async def get_repository_session(session_id: str):
    provider = get_provider()
    record = provider.get_by_id(RepositorySessionRecord, session_id)
    if not record:
        raise HTTPException(404, detail=f"Repository session {session_id} not found")
    import dataclasses
    data = dataclasses.asdict(record) if hasattr(record, '__dataclass_fields__') else vars(record)
    return GenericObjectDTO(**data)


@router.get("/commits")
async def list_commits(repository_session_id: Optional[str] = None, limit: int = 100, offset: int = 0):
    provider = get_provider()
    records = provider.query(CommitRecord, limit=limit, offset=offset)
    return {"items": [_summarize(r) for r in records], "total": provider.count(CommitRecord)}


@router.get("/developers")
async def list_developers(repository_session_id: Optional[str] = None, limit: int = 100, offset: int = 0):
    provider = get_provider()
    records = provider.query(DeveloperRecord, limit=limit, offset=offset)
    return {"items": [_summarize(r) for r in records], "total": provider.count(DeveloperRecord)}


@router.get("/developers/{dev_id}", response_model=GenericObjectDTO)
async def get_developer(dev_id: str):
    provider = get_provider()
    record = provider.get_by_id(DeveloperRecord, dev_id)
    if not record:
        raise HTTPException(404, detail="Developer not found")
    import dataclasses
    data = dataclasses.asdict(record) if hasattr(record, '__dataclass_fields__') else vars(record)
    return GenericObjectDTO(**data)


@router.get("/files")
async def list_files(repository_session_id: Optional[str] = None, limit: int = 100, offset: int = 0):
    provider = get_provider()
    records = provider.query(FileRecord, limit=limit, offset=offset)
    return {"items": [_summarize(r) for r in records], "total": provider.count(FileRecord)}


@router.get("/measurements")
async def list_measurements(metric_name: Optional[str] = None, limit: int = 100, offset: int = 0):
    provider = get_provider()
    records = provider.query(MeasurementRecord, limit=limit, offset=offset)
    return {"items": [_summarize(r) for r in records], "total": provider.count(MeasurementRecord)}


@router.get("/measurements/{measurement_id}", response_model=GenericObjectDTO)
async def get_measurement(measurement_id: str):
    """Measurement Explorer: full transparency including formula, inputs, intermediate values."""
    provider = get_provider()
    record = provider.get_by_id(MeasurementRecord, measurement_id)
    if not record:
        raise HTTPException(404, detail="Measurement not found")
    # Include algorithm metadata
    from app.core.algorithms.registry import get_algorithm_registry
    algo = get_algorithm_registry().get(record.identity.algorithm_version or "")
    result = {
        "object_id": record.identity.object_id,
        "object_type": record.identity.object_type,
        "version": record.identity.version,
        "created_at": record.identity.created_at,
        "algorithm_version": record.identity.algorithm_version,
        "execution_id": record.identity.execution_id,
        "metric_name": record.metric_name,
        "metric_value": record.metric_value,
        "confidence": record.confidence,
        "formula": record.formula,
        "inputs": record.inputs,
        "intermediate_values": record.intermediate_values,
        "normalization": record.normalization,
        "thresholds": record.thresholds,
        "subject_id": record.subject_id,
        "subject_type": record.subject_type,
        "evidence_ids": record.evidence_ids,
        "previous_version_id": record.previous_version_id,
        "algorithm": {
            "algorithm_id": algo.algorithm_id,
            "name": algo.name,
            "version": algo.version,
            "description": algo.description,
            "formula": algo.formula,
            "inputs": [{"name": i.name, "type": i.type, "description": i.description} for i in algo.inputs],
            "outputs": [{"name": o.name, "type": o.type, "description": o.description} for o in algo.outputs],
            "avg_latency_ms": algo.avg_latency_ms,
            "execution_count": algo.execution_count,
            "failure_count": algo.failure_count,
        } if algo else None,
    }
    return GenericObjectDTO(**result)


@router.get("/evidence")
async def list_evidence(evidence_type: Optional[str] = None, limit: int = 100, offset: int = 0):
    provider = get_provider()
    records = provider.query(EvidenceRecord, limit=limit, offset=offset)
    return {"items": [_summarize(r) for r in records], "total": provider.count(EvidenceRecord)}


@router.get("/evidence/{evidence_id}", response_model=GenericObjectDTO)
async def get_evidence(evidence_id: str):
    provider = get_provider()
    record = provider.get_by_id(EvidenceRecord, evidence_id)
    if not record:
        raise HTTPException(404, detail="Evidence not found")
    return {
        "object_id": record.identity.object_id,
        "version": record.identity.version,
        "created_at": record.identity.created_at,
        "evidence_type": record.evidence_type,
        "summary": record.summary,
        "content": record.content,
        "confidence": record.confidence,
        "measurement_ids": record.measurement_ids,
        "commit_ids": record.commit_ids,
        "subject_id": record.subject_id,
        "subject_type": record.subject_type,
        "previous_version_id": record.previous_version_id,
    }
    return GenericObjectDTO(**res)


@router.get("/executions")
async def list_executions(limit: int = 50, offset: int = 0):
    provider = get_provider()
    records = provider.query(ExecutionRecord, limit=limit, offset=offset)
    return {"items": [_summarize(r) for r in records], "total": provider.count(ExecutionRecord)}


@router.get("/executions/{execution_id}", response_model=GenericObjectDTO)
async def get_execution(execution_id: str):
    """Execution Explorer: full stage-by-stage breakdown."""
    provider = get_provider()
    record = provider.get_by_id(ExecutionRecord, execution_id)
    if not record:
        raise HTTPException(404, detail="Execution not found")
    # Also fetch related reasoning
    rule_executions = provider.query(RuleExecutionRecord, limit=20)
    related = [r for r in rule_executions if r.identity.execution_id == execution_id]
    return {
        "object_id": record.identity.object_id,
        "created_at": record.identity.created_at,
        "query": record.query,
        "intent": record.intent,
        "status": record.status,
        "planner_output": record.planner_output,
        "capabilities_used": record.capabilities_used,
        "measurement_ids": record.measurement_ids,
        "evidence_ids": record.evidence_ids,
        "reasoning_ids": record.reasoning_ids,
        "answer": record.answer,
        "confidence": record.confidence,
        "total_latency_ms": record.total_latency_ms,
        "stage_latencies": record.stage_latencies,
        "completed_at": record.completed_at,
        "reasoning": [
            {
                "reasoning_id": r.identity.object_id,
                "reasoning_type": "rule_execution",
                "conclusion": str(r.outputs),
                "confidence": r.confidence,
                "rules_fired": [r.rule_id],
                "business_impact": r.outputs.get("impact", "low"),
            }
            for r in related
        ],
    }
    return GenericObjectDTO(**res)


@router.get("/datasets")
async def list_datasets(limit: int = 50, offset: int = 0):
    provider = get_provider()
    records = provider.query(DatasetRecord, limit=limit, offset=offset)
    return {"items": [_summarize(r) for r in records], "total": provider.count(DatasetRecord)}
