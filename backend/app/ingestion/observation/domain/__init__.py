from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from app.domain.entity_ref import EntityRef


class ObservationType(Enum):
    # --- Software Engineering (original) ---
    COMMIT = "commit"
    PULL_REQUEST = "pull_request"
    ISSUE = "issue"
    REVIEW = "review"
    COMMENT = "comment"
    MERGE = "merge"
    BUILD = "build"
    DEPLOYMENT = "deployment"
    INCIDENT = "incident"
    RELEASE = "release"
    RUNTIME = "runtime"
    SECURITY = "security"
    TEST = "test"
    CLOUD = "cloud"
    INFRASTRUCTURE = "infrastructure"
    AI_SYSTEM = "ai_system"
    DOCUMENTATION = "documentation"

    # --- Industrial ---
    MAINTENANCE = "maintenance"
    INSPECTION_EVENT = "inspection_event"
    FAILURE = "failure"
    WORK_ORDER = "work_order"
    RECOMMENDATION_EVENT = "recommendation_event"
    PARAMETER_READING = "parameter_reading"
    DOCUMENT_INGESTION = "document_ingestion"
    NEAR_MISS = "near_miss"
    AUDIT = "audit"
    QUALITY_NCR = "quality_ncr"
    COMPLIANCE_EVENT = "compliance_event"


class ObservationCategory(Enum):
    # --- Software Engineering (original) ---
    SOURCE_CONTROL = "source_control"
    CODE_REVIEW = "code_review"
    CI_CD = "ci_cd"
    RUNTIME = "runtime"
    SECURITY = "security"
    TESTING = "testing"
    CLOUD = "cloud"
    INFRASTRUCTURE = "infrastructure"
    DOCUMENTATION = "documentation"
    AI = "ai"
    PROJECT_MANAGEMENT = "project_management"

    # --- Industrial ---
    MAINTENANCE = "maintenance"
    INSPECTION = "inspection"
    OPERATIONS = "operations"
    SAFETY = "safety"
    QUALITY = "quality"
    COMPLIANCE = "compliance"
    ENGINEERING = "engineering"
    RELIABILITY = "reliability"


class ObservationLifecycle(Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ProcessingMode(str, Enum):
    LIVE = "live"
    REPLAY = "replay"


@dataclass(frozen=True)
class ObservationProvenance:
    source_platform: str
    source_adapter: str
    source_record_id: str
    fetched_at: datetime | None = None
    adapter_version: str = "1.0"
    replay_ref: str | None = None


@dataclass(frozen=True)
class ObservationContext:
    repository: str | None = None
    organization: str | None = None
    branch: str | None = None
    tenant_id: str | None = None
    labels: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FileChangeFacts:
    path: str
    status: str
    additions: int = 0
    deletions: int = 0
    changes: int = 0
    previous_path: str | None = None
    patch: str | None = None


@dataclass(frozen=True)
class CommitFacts:
    commit_id: str
    message: str
    author_name: str | None
    author_email: str | None
    authored_at: datetime
    committer_name: str | None = None
    committer_email: str | None = None
    committed_at: datetime | None = None
    parent_ids: tuple[str, ...] = ()
    total_additions: int = 0
    total_deletions: int = 0
    total_changes: int = 0
    files: tuple[FileChangeFacts, ...] = ()
    signature_verified: bool | None = None


@dataclass(frozen=True)
class PullRequestFacts:
    pull_request_id: str
    title: str
    state: str
    author: str | None
    created_at: datetime
    updated_at: datetime | None = None
    closed_at: datetime | None = None
    merged_at: datetime | None = None
    source_branch: str | None = None
    target_branch: str | None = None
    commit_ids: tuple[str, ...] = ()
    changed_files: int | None = None


@dataclass(frozen=True)
class IssueFacts:
    issue_id: str
    title: str
    state: str
    author: str | None
    created_at: datetime
    updated_at: datetime | None = None
    closed_at: datetime | None = None
    labels: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReviewFacts:
    review_id: str
    subject_id: str
    reviewer: str | None
    state: str
    submitted_at: datetime | None = None
    comment_count: int = 0


@dataclass(frozen=True)
class CommentFacts:
    comment_id: str
    subject_id: str
    author: str | None
    body: str
    created_at: datetime
    updated_at: datetime | None = None


@dataclass(frozen=True)
class MergeFacts:
    merge_id: str
    source_ref: str
    target_ref: str
    merged_by: str | None
    merged_at: datetime
    commit_id: str | None = None


@dataclass(frozen=True)
class BuildFacts:
    build_id: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    duration_seconds: float | None = None


@dataclass(frozen=True)
class DeploymentFacts:
    deployment_id: str
    environment: str
    status: str
    deployed_at: datetime
    version: str | None = None


@dataclass(frozen=True)
class IncidentFacts:
    incident_id: str
    title: str
    severity: str
    status: str
    started_at: datetime
    resolved_at: datetime | None = None
    service: str | None = None


@dataclass(frozen=True)
class ReleaseFacts:
    release_id: str
    version: str
    status: str
    released_at: datetime
    author: str | None = None


@dataclass(frozen=True)
class RuntimeFacts:
    runtime_id: str
    observed_at: datetime
    service: str
    status: str
    counters: Mapping[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class SecurityFacts:
    finding_id: str
    scanner: str
    observed_at: datetime
    category: str
    state: str
    affected_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class TestFacts:
    test_run_id: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    passed: int = 0
    failed: int = 0
    skipped: int = 0


@dataclass(frozen=True)
class CloudFacts:
    resource_id: str
    resource_type: str
    observed_at: datetime
    state: str
    region: str | None = None


@dataclass(frozen=True)
class InfrastructureFacts:
    resource_id: str
    resource_type: str
    observed_at: datetime
    state: str
    location: str | None = None


@dataclass(frozen=True)
class DocumentationFacts:
    document_id: str
    path: str
    observed_at: datetime
    state: str
    title: str | None = None


@dataclass(frozen=True)
class AISystemFacts:
    system_id: str
    observed_at: datetime
    provider: str
    model: str
    state: str


# ---------------------------------------------------------------------------
# Industrial CanonicalFacts
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MaintenanceActionFacts:
    """Facts from a maintenance action or work order."""
    work_order_id: str
    asset_id: str | None = None
    equipment_tag: str | None = None
    action_type: str | None = None
    description: str = ""
    performed_by: str | None = None
    performed_at: datetime | None = None
    status: str = "COMPLETED"
    findings: tuple[str, ...] = ()
    parts_used: tuple[str, ...] = ()
    labor_hours: float | None = None
    cost: float | None = None
    source_document_id: str | None = None


@dataclass(frozen=True)
class InspectionFacts:
    """Facts from an inspection."""
    inspection_id: str
    asset_id: str | None = None
    equipment_tag: str | None = None
    inspection_type: str | None = None
    inspector: str | None = None
    inspection_date: datetime | None = None
    result: str = "SATISFACTORY"
    findings: tuple[str, ...] = ()
    measurements: tuple[str, ...] = ()
    recommendations: tuple[str, ...] = ()
    severity: str | None = None
    source_document_id: str | None = None


@dataclass(frozen=True)
class FailureEventFacts:
    """Facts from a failure event."""
    failure_id: str
    asset_id: str | None = None
    equipment_tag: str | None = None
    failure_mode: str | None = None
    failure_cause: str | None = None
    description: str = ""
    failure_date: datetime | None = None
    severity: str | None = None
    downtime_hours: float | None = None
    resolution: str | None = None
    source_document_id: str | None = None


@dataclass(frozen=True)
class RecommendationFacts:
    """Facts from a maintenance or engineering recommendation."""
    recommendation_id: str
    asset_id: str | None = None
    equipment_tag: str | None = None
    description: str = ""
    action_required: str = ""
    priority: str | None = None
    status: str = "OPEN"
    recommended_by: str | None = None
    recommended_date: datetime | None = None
    due_date: datetime | None = None
    source_document_id: str | None = None


@dataclass(frozen=True)
class ParameterReadingFacts:
    """Facts from an operating parameter reading."""
    reading_id: str
    asset_id: str | None = None
    equipment_tag: str | None = None
    parameter_name: str = ""
    value: float = 0.0
    unit: str = ""
    recorded_at: datetime | None = None
    normal_range_low: float | None = None
    normal_range_high: float | None = None
    is_abnormal: bool = False
    source_document_id: str | None = None


@dataclass(frozen=True)
class DocumentIngestionFacts:
    """Facts from a document ingestion event."""
    document_id: str
    document_name: str = ""
    document_type: str = ""
    document_format: str = ""
    file_hash: str = ""
    page_count: int = 0
    chunk_count: int = 0
    entity_count: int = 0
    ingested_at: datetime | None = None


CanonicalFacts = (
    # Software Engineering
    CommitFacts
    | PullRequestFacts
    | IssueFacts
    | ReviewFacts
    | CommentFacts
    | MergeFacts
    | BuildFacts
    | DeploymentFacts
    | IncidentFacts
    | ReleaseFacts
    | RuntimeFacts
    | SecurityFacts
    | TestFacts
    | CloudFacts
    | InfrastructureFacts
    | DocumentationFacts
    | AISystemFacts
    # Industrial
    | MaintenanceActionFacts
    | InspectionFacts
    | FailureEventFacts
    | RecommendationFacts
    | ParameterReadingFacts
    | DocumentIngestionFacts
)


@dataclass(frozen=True)
class Observation:
    observation_id: str
    trace_id: str
    correlation_id: str
    timestamp: datetime
    observation_type: ObservationType
    observation_category: ObservationCategory
    source_platform: str
    source_adapter: str
    version: str
    lifecycle: ObservationLifecycle
    actors: tuple[EntityRef, ...]
    targets: tuple[EntityRef, ...]
    provenance: ObservationProvenance
    context: ObservationContext
    facts: CanonicalFacts
    processing_mode: ProcessingMode = ProcessingMode.LIVE
