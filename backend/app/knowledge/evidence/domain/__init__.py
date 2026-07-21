from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from app.intelligence.measurement.domain import Measurement


class EvidenceSeverity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def rank(self) -> int:
        return {
            EvidenceSeverity.INFO: 0,
            EvidenceSeverity.LOW: 1,
            EvidenceSeverity.MEDIUM: 2,
            EvidenceSeverity.HIGH: 3,
            EvidenceSeverity.CRITICAL: 4,
        }[self]


class EvidencePriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

    def rank(self) -> int:
        return {
            EvidencePriority.LOW: 0,
            EvidencePriority.MEDIUM: 1,
            EvidencePriority.HIGH: 2,
            EvidencePriority.URGENT: 3,
        }[self]


class EvidenceStatus(Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    CONFLICTED = "conflicted"
    REJECTED = "rejected"


class EvidenceLifecycle(Enum):
    DRAFT = "draft"
    EXPERIMENTAL = "experimental"
    VALIDATED = "validated"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class EvidenceValidationStatus(Enum):
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    NOT_RUN = "not_run"


@dataclass(frozen=True)
class TimeWindow:
    started_at: datetime | None = None
    ended_at: datetime | None = None


@dataclass(frozen=True)
class EvidenceMeasurementRef:
    id: str
    definition_id: str
    name: str
    value: float
    confidence: float
    uncertainty_variance: float
    quality_score: float
    source_system: str
    tenant_id: str | None
    timestamp: datetime
    validation_status: str
    entity_ids: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    calibration: Any | None = None

    @classmethod
    def from_measurement(
        cls,
        measurement: Measurement,
    ) -> "EvidenceMeasurementRef":
        return cls(
            id=measurement.id,
            definition_id=measurement.definition.id,
            name=measurement.definition.name,
            value=measurement.value,
            confidence=measurement.confidence,
            uncertainty_variance=measurement.uncertainty.variance,
            quality_score=measurement.quality_score,
            source_system=measurement.provenance.source_system,
            tenant_id=measurement.provenance.tenant_id,
            timestamp=measurement.timestamp,
            validation_status=measurement.validation_status.value,
            entity_ids=measurement.provenance.source_entity_ids,
            metadata=measurement.metadata,
            calibration=measurement.calibration,
        )


@dataclass(frozen=True)
class BenchmarkContext:
    cohort: str | None = None
    percentile: float | None = None
    interpretation: str | None = None
    quality: float = 1.0
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class HistoricalContext:
    persistence: float = 0.0
    novelty: float = 0.0
    trend: str = "unknown"
    consistency: float = 1.0
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvidenceProvenance:
    source_layer: str
    generated_by: str
    tenant_id: str | None = None
    measurement_ids: tuple[str, ...] = ()
    evidence_definition_id: str | None = None
    pipeline_version: str = "evidence.v1"
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvidenceLineage:
    parent_evidence_ids: tuple[str, ...] = ()
    source_measurement_ids: tuple[str, ...] = ()
    derived_from: tuple[str, ...] = ()
    graph_node_id: str | None = None


@dataclass(frozen=True)
class EvidenceTraceability:
    synthesis_rule_ids: tuple[str, ...] = ()
    confidence_factors: Mapping[str, float] = field(default_factory=dict)
    validation_checks: tuple[str, ...] = ()
    explanation: str = ""


@dataclass(frozen=True)
class EvidenceValidationResult:
    name: str
    status: EvidenceValidationStatus
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    name: str
    category: str
    description: str
    severity: EvidenceSeverity
    priority: EvidencePriority
    status: EvidenceStatus
    confidence: float
    uncertainty: float
    quality: float
    strength: float
    supporting_measurements: tuple[EvidenceMeasurementRef, ...]
    contradicting_measurements: tuple[EvidenceMeasurementRef, ...]
    benchmark_context: BenchmarkContext
    historical_context: HistoricalContext
    time_window: TimeWindow
    provenance: EvidenceProvenance
    lineage: EvidenceLineage
    traceability: EvidenceTraceability
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]
    validation_results: tuple[EvidenceValidationResult, ...]
    version: str
    lifecycle: EvidenceLifecycle
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def is_valid_for_expertise(
        self,
    ) -> bool:
        return (
            self.status == EvidenceStatus.VALIDATED
            and self.lifecycle
            not in {
                EvidenceLifecycle.DEPRECATED,
                EvidenceLifecycle.ARCHIVED,
            }
            and all(
                result.status
                != EvidenceValidationStatus.FAILED
                for result in self.validation_results
            )
        )

