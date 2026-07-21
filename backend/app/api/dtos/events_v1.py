"""
PIA Versioned WebSocket Event Contracts — Schema v1.

These are the ONLY types the Developer Console WebSocket endpoint may emit.
The browser subscribes to these stable, typed contracts.
No arbitrary Python objects or engine internals may pass through this boundary.

Every event carries:
  - schema_version: "v1" (bump to v2 if breaking changes occur)
  - event_type: stable string enum
  - occurred_at: ISO 8601 UTC timestamp

Clients should switch on event_type, ignore unknown types gracefully,
and reject events whose schema_version differs from what they support.
"""
from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


def _now() -> str:
    return datetime.datetime.utcnow().isoformat() + "Z"


# ─────────────────────────────────────────────────────────
# Base Contract
# ─────────────────────────────────────────────────────────

class BaseEvent(BaseModel):
    schema_version: str = "v1"
    event_type: str
    occurred_at: str = Field(default_factory=_now)
    workspace_id: Optional[str] = None
    repository_session_id: Optional[str] = None
    execution_id: Optional[str] = None


# ─────────────────────────────────────────────────────────
# Sync Events
# ─────────────────────────────────────────────────────────

class SyncStartedEvent(BaseEvent):
    event_type: str = "sync.started"
    repository: str
    sync_mode: str  # full | incremental | replay | rebuild_projections
    source_plugin: str = "github"


class SyncProgressEvent(BaseEvent):
    event_type: str = "sync.progress"
    repository: str
    commits_processed: int
    commits_total: int
    developers_found: int
    files_processed: int
    current_operation: str


class SyncCompletedEvent(BaseEvent):
    event_type: str = "sync.completed"
    repository: str
    commits_ingested: int
    developers_ingested: int
    files_ingested: int
    duration_ms: float
    triggered_projections: List[str] = Field(default_factory=list)


class SyncFailedEvent(BaseEvent):
    event_type: str = "sync.failed"
    repository: str
    error: str
    recoverable: bool = True


# ─────────────────────────────────────────────────────────
# Measurement Events
# ─────────────────────────────────────────────────────────

class MeasurementCreatedEvent(BaseEvent):
    event_type: str = "measurement.created"
    measurement_id: str
    metric_name: str
    algorithm_id: str
    algorithm_version: str
    subject_type: str
    subject_id: str
    value: float
    confidence: float


class MeasurementVersionedEvent(BaseEvent):
    event_type: str = "measurement.versioned"
    new_measurement_id: str
    previous_measurement_id: str
    metric_name: str
    algorithm_id: str
    new_version: int
    value_delta: float


# ─────────────────────────────────────────────────────────
# Evidence Events
# ─────────────────────────────────────────────────────────

class EvidenceCreatedEvent(BaseEvent):
    event_type: str = "evidence.created"
    evidence_id: str
    evidence_type: str
    subject_type: str
    subject_id: str
    confidence: float
    measurement_count: int


# ─────────────────────────────────────────────────────────
# Projection Events
# ─────────────────────────────────────────────────────────

class ProjectionBuildStartedEvent(BaseEvent):
    event_type: str = "projection.build_started"
    projection_id: str
    projection_name: str
    trigger_event: str
    full_rebuild: bool = False


class ProjectionBuildCompletedEvent(BaseEvent):
    event_type: str = "projection.build_completed"
    projection_id: str
    projection_name: str
    duration_ms: float
    node_count: int = 0
    edge_count: int = 0
    record_count: int = 0


class ProjectionBuildFailedEvent(BaseEvent):
    event_type: str = "projection.build_failed"
    projection_id: str
    projection_name: str
    error: str


# ─────────────────────────────────────────────────────────
# Execution Events
# ─────────────────────────────────────────────────────────

class ExecutionStartedEvent(BaseEvent):
    event_type: str = "execution.started"
    query: str
    intent: str = ""


class CapabilityStartedEvent(BaseEvent):
    event_type: str = "capability.started"
    capability_name: str
    inputs_summary: Dict[str, Any] = Field(default_factory=dict)


class CapabilityCompletedEvent(BaseEvent):
    event_type: str = "capability.completed"
    capability_name: str
    latency_ms: float
    confidence: float = 0.0
    output_summary: str = ""


class ReasoningCompletedEvent(BaseEvent):
    event_type: str = "reasoning.completed"
    conclusion_summary: str
    confidence: float
    rules_fired: List[str] = Field(default_factory=list)
    evidence_count: int = 0


class ExecutionCompletedEvent(BaseEvent):
    event_type: str = "execution.completed"
    status: str
    answer_summary: str
    total_latency_ms: float
    stage_latencies: Dict[str, float] = Field(default_factory=dict)


class ExecutionFailedEvent(BaseEvent):
    event_type: str = "execution.failed"
    error: str
    failed_stage: str
    recoverable: bool = False


# ─────────────────────────────────────────────────────────
# Health Events
# ─────────────────────────────────────────────────────────

class HealthChangedEvent(BaseEvent):
    event_type: str = "health.changed"
    component: str
    previous_status: str
    current_status: str
    details: str = ""


# ─────────────────────────────────────────────────────────
# Union type for dispatcher
# ─────────────────────────────────────────────────────────

ALL_EVENT_TYPES = [
    SyncStartedEvent, SyncProgressEvent, SyncCompletedEvent, SyncFailedEvent,
    MeasurementCreatedEvent, MeasurementVersionedEvent,
    EvidenceCreatedEvent,
    ProjectionBuildStartedEvent, ProjectionBuildCompletedEvent, ProjectionBuildFailedEvent,
    ExecutionStartedEvent, CapabilityStartedEvent, CapabilityCompletedEvent,
    ReasoningCompletedEvent, ExecutionCompletedEvent, ExecutionFailedEvent,
    HealthChangedEvent,
]
