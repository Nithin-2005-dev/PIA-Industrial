"""
PIA Canonical Operational Store Models.

These are the immutable canonical records stored in the Operational Store.
They are NOT the execution engine. The Platform Runtime and Reasoning Engine
consume these records and produce new versions — they never overwrite existing ones.

Every record has a GlobalIdentity: object_id, type, version, created_at,
algorithm_version, dataset_id, workspace_id, execution_id, and parent_ids.
This enables complete lineage tracing from raw repository event to final presentation.
"""
from __future__ import annotations

import uuid
import datetime
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _new_id() -> str:
    return str(uuid.uuid4())


def _now() -> str:
    return datetime.datetime.utcnow().isoformat() + "Z"


# ─────────────────────────────────────────────────────────
# Global Identity (every entity carries this)
# ─────────────────────────────────────────────────────────

@dataclass
class GlobalIdentity:
    object_id: str = field(default_factory=_new_id)
    object_type: str = ""
    version: int = 1
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    algorithm_version: Optional[str] = None
    dataset_id: Optional[str] = None
    workspace_id: Optional[str] = None
    execution_id: Optional[str] = None
    parent_ids: List[str] = field(default_factory=list)


# ─────────────────────────────────────────────────────────
# Workspace & Repository Session
# ─────────────────────────────────────────────────────────

@dataclass
class WorkspaceRecord:
    """A logical workspace grouping one or more repository sessions."""
    identity: GlobalIdentity = field(default_factory=lambda: GlobalIdentity(object_type="workspace"))
    name: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def object_id(self) -> str:
        return self.identity.object_id


@dataclass
class RepositorySessionRecord:
    """
    A snapshot session for a specific repository, branch, and commit window.
    Allows comparing different branches or commit ranges side-by-side.
    """
    identity: GlobalIdentity = field(default_factory=lambda: GlobalIdentity(object_type="repository_session"))
    workspace_id: str = ""
    repository: str = ""          # e.g. "facebook/react"
    branch: str = "main"
    commit_window: int = 50
    head_commit_sha: str = ""
    languages: List[str] = field(default_factory=list)
    sync_status: str = "pending"  # pending | syncing | healthy | failed
    last_synced_at: Optional[str] = None
    source_plugin: str = "github" # github | gitlab | local_git
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def object_id(self) -> str:
        return self.identity.object_id


# ─────────────────────────────────────────────────────────
# Commit
# ─────────────────────────────────────────────────────────

@dataclass
class CommitRecord:
    identity: GlobalIdentity = field(default_factory=lambda: GlobalIdentity(object_type="commit"))
    repository_session_id: str = ""
    sha: str = ""
    message: str = ""
    author_email: str = ""
    author_name: str = ""
    timestamp: str = ""
    files_changed: int = 0
    additions: int = 0
    deletions: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def object_id(self) -> str:
        return self.identity.object_id


# ─────────────────────────────────────────────────────────
# Developer
# ─────────────────────────────────────────────────────────

@dataclass
class DeveloperRecord:
    identity: GlobalIdentity = field(default_factory=lambda: GlobalIdentity(object_type="developer"))
    repository_session_id: str = ""
    email: str = ""
    login: str = ""
    display_name: str = ""
    commit_count: int = 0
    first_commit_at: Optional[str] = None
    last_commit_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def object_id(self) -> str:
        return self.identity.object_id


# ─────────────────────────────────────────────────────────
# File
# ─────────────────────────────────────────────────────────

@dataclass
class FileRecord:
    identity: GlobalIdentity = field(default_factory=lambda: GlobalIdentity(object_type="file"))
    repository_session_id: str = ""
    path: str = ""
    language: str = ""
    module: str = ""
    package: str = ""
    size_bytes: int = 0
    line_count: int = 0
    last_modified_sha: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def object_id(self) -> str:
        return self.identity.object_id


# ─────────────────────────────────────────────────────────
# Measurement (versioned — never overwrite, always create v+1)
# ─────────────────────────────────────────────────────────

@dataclass
class MeasurementRecord:
    """
    A versioned deterministic measurement. New algorithm runs produce v+1, never mutate v1.
    Exposes full computational transparency: formula, inputs, intermediate values, confidence.
    """
    identity: GlobalIdentity = field(default_factory=lambda: GlobalIdentity(object_type="measurement"))
    repository_session_id: str = ""
    metric_name: str = ""          # e.g. "bus_factor", "ownership_gini"
    metric_value: float = 0.0
    confidence: float = 0.0
    formula: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    intermediate_values: Dict[str, Any] = field(default_factory=dict)
    normalization: str = ""
    thresholds: Dict[str, float] = field(default_factory=dict)
    subject_id: str = ""           # e.g. developer_id, file_id
    subject_type: str = ""         # developer | file | module | repository
    evidence_ids: List[str] = field(default_factory=list)
    previous_version_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def object_id(self) -> str:
        return self.identity.object_id


# ─────────────────────────────────────────────────────────
# Evidence (versioned)
# ─────────────────────────────────────────────────────────

@dataclass
class EvidenceRecord:
    """
    A versioned evidence object. Raw signals synthesized into structured evidence.
    Linked to its source measurements and parent commits.
    """
    identity: GlobalIdentity = field(default_factory=lambda: GlobalIdentity(object_type="evidence"))
    repository_session_id: str = ""
    evidence_type: str = ""        # ownership | bus_factor | risk | expertise | ...
    summary: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    measurement_ids: List[str] = field(default_factory=list)
    commit_ids: List[str] = field(default_factory=list)
    subject_id: str = ""
    subject_type: str = ""
    previous_version_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def object_id(self) -> str:
        return self.identity.object_id


# ─────────────────────────────────────────────────────────
# Execution Record
# ─────────────────────────────────────────────────────────

@dataclass
class ExecutionRecord:
    """
    A complete execution record. Every stage is stored so executions are fully replayable.
    """
    identity: GlobalIdentity = field(default_factory=lambda: GlobalIdentity(object_type="execution"))
    repository_session_id: str = ""
    query: str = ""
    intent: str = ""
    status: str = "pending"         # pending | running | success | failed
    planner_output: Dict[str, Any] = field(default_factory=dict)
    capabilities_used: List[str] = field(default_factory=list)
    measurement_ids: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    reasoning_ids: List[str] = field(default_factory=list)
    answer: str = ""
    confidence: float = 0.0
    total_latency_ms: float = 0.0
    stage_latencies: Dict[str, float] = field(default_factory=dict)
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def object_id(self) -> str:
        return self.identity.object_id


# ─────────────────────────────────────────────────────────
# Fact Record
# ─────────────────────────────────────────────────────────

@dataclass
class FactRecord:
    """A deterministic fact synthesized from Evidence and Measurements."""
    identity: GlobalIdentity = field(default_factory=lambda: GlobalIdentity(object_type="fact"))
    repository_session_id: str = ""
    fact_type: str = ""
    confidence: float = 0.0
    measurement_ids: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    knowledge_node_ids: List[str] = field(default_factory=list)
    hash: str = ""
    
    @property
    def object_id(self) -> str:
        return self.identity.object_id


# ─────────────────────────────────────────────────────────
# Rule Evaluation & Execution Records
# ─────────────────────────────────────────────────────────

@dataclass
class RuleEvaluationRecord:
    """Records every rule that was evaluated, including failures."""
    identity: GlobalIdentity = field(default_factory=lambda: GlobalIdentity(object_type="rule_evaluation"))
    repository_session_id: str = ""
    rule_id: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    preconditions: Dict[str, Any] = field(default_factory=dict)
    passed: bool = False
    reason_if_failed: str = ""
    latency_ms: float = 0.0
    
    @property
    def object_id(self) -> str:
        return self.identity.object_id


@dataclass
class RuleExecutionRecord:
    """Records every rule that fired and produced outputs."""
    identity: GlobalIdentity = field(default_factory=lambda: GlobalIdentity(object_type="rule_execution"))
    repository_session_id: str = ""
    rule_id: str = ""
    outputs: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    execution_hash: str = ""
    
    @property
    def object_id(self) -> str:
        return self.identity.object_id


# ─────────────────────────────────────────────────────────
# Reasoning Graph Projection Record
# ─────────────────────────────────────────────────────────

@dataclass
class ReasoningGraphProjectionRecord:
    """The final deterministic projection output of the Reasoning Builder."""
    identity: GlobalIdentity = field(default_factory=lambda: GlobalIdentity(object_type="reasoning_projection"))
    projection_id: str = field(default_factory=_new_id)
    schema_version: str = "1.0"
    builder_version: str = "1.0"
    dataset_id: str = ""
    execution_id: str = ""
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    edges: List[Dict[str, Any]] = field(default_factory=list)
    measurement_hash: str = ""
    evidence_hash: str = ""
    fact_hash: str = ""
    rule_hash: str = ""
    inference_hash: str = ""
    projection_hash: str = ""
    
    @property
    def object_id(self) -> str:
        return self.identity.object_id


# ─────────────────────────────────────────────────────────
# Dataset
# ─────────────────────────────────────────────────────────

@dataclass
class DatasetRecord:
    """An offline snapshot dataset for deterministic benchmarking."""
    identity: GlobalIdentity = field(default_factory=lambda: GlobalIdentity(object_type="dataset"))
    name: str = ""
    repository: str = ""
    snapshot_sha: str = ""
    manifest: Dict[str, Any] = field(default_factory=dict)
    checksums: Dict[str, str] = field(default_factory=dict)
    coverage: float = 0.0
    health_status: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def object_id(self) -> str:
        return self.identity.object_id


# ─────────────────────────────────────────────────────────
# Projections
# ─────────────────────────────────────────────────────────

@dataclass
class KnowledgeGraphProjectionRecord:
    """A persisted, immutable, versioned Knowledge Graph Projection."""
    identity: GlobalIdentity = field(default_factory=lambda: GlobalIdentity(object_type="projection"))
    projection_id: str = "" # Content-addressed SHA-256 hash
    projection_type: str = "KnowledgeGraph"
    projection_hash: str = "" # SHA-256 of canonical serialized graph
    builder_version: str = "1.0.0"
    schema_version: str = "1.0.0"
    dataset_id: Optional[str] = None
    execution_id: Optional[str] = None
    parent_projection_id: Optional[str] = None
    
    # Structural details
    node_count: int = 0
    edge_count: int = 0
    
    # Analytics / Stats
    statistics: Dict[str, Any] = field(default_factory=dict)
    
    # Layered Validation Results
    validation_report: Dict[str, Any] = field(default_factory=dict)
    
    # Determinism
    replay_hash: Optional[str] = None
    measurement_hash: str = ""
    evidence_hash: str = ""
    
    # Builder Metadata
    builder: str = "KnowledgeGraphProjectionBuilder"
    git_commit: str = ""
    configuration: Dict[str, Any] = field(default_factory=dict)
    runtime_env: str = ""
    build_duration_ms: float = 0.0
    
    # The actual Canonical DTO Graph
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    edges: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def object_id(self) -> str:
        return self.identity.object_id


# ─────────────────────────────────────────────────────────
# Registry of all model types for Universal Search
# ─────────────────────────────────────────────────────────

ALL_RECORD_TYPES = [
    WorkspaceRecord,
    RepositorySessionRecord,
    CommitRecord,
    DeveloperRecord,
    FileRecord,
    MeasurementRecord,
    EvidenceRecord,
    ExecutionRecord,
    FactRecord,
    RuleEvaluationRecord,
    RuleExecutionRecord,
    ReasoningGraphProjectionRecord,
    DatasetRecord,
    KnowledgeGraphProjectionRecord,
]

RECORD_TYPE_MAP: Dict[str, type] = {
    cls.__dataclass_fields__["identity"].default_factory().object_type
    if hasattr(cls.__dataclass_fields__["identity"].default_factory(), "object_type")
    else cls.__name__.lower(): cls
    for cls in ALL_RECORD_TYPES
}
