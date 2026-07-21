from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class MeasurementUnit(Enum):
    COUNT = "count"
    RATIO = "ratio"
    PERCENT = "percent"
    SECONDS = "seconds"
    BYTES = "bytes"
    LOC = "loc"
    COMPLEXITY = "complexity"
    ENTROPY = "entropy"
    PROBABILITY = "probability"
    COST = "cost"
    CURRENCY = "currency"
    FREQUENCY = "frequency"
    DENSITY = "density"
    GRAPH = "graph"
    SCORE = "score"
    CUSTOM = "custom"


class ValidationStatus(Enum):
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    NOT_RUN = "not_run"


@dataclass(frozen=True)
class ExpectedRange:
    minimum: float | None = None
    maximum: float | None = None
    inclusive: bool = True


@dataclass(frozen=True)
class MeasurementReference:
    title: str
    source: str
    identifier: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class MeasurementConcept:
    id: str
    display_name: str
    scientific_meaning: str
    category: str
    parent_id: str | None = None
    dimensions: tuple[str, ...] = ()
    references: tuple[MeasurementReference, ...] = ()


@dataclass(frozen=True)
class MeasurementDefinition:
    id: str
    name: str
    description: str
    unit: MeasurementUnit
    version: str
    minimum: float | None = None
    maximum: float | None = None
    tags: tuple[str, ...] = ()
    concept_id: str | None = None
    category: str = "general"
    expected_range: ExpectedRange | None = None
    formula: str | None = None
    dependencies: tuple[str, ...] = ()
    required_signals: tuple[str, ...] = ()
    confidence_model: str = "default_factor_model"
    validator: str = "default_validation_pipeline"
    normalizer: str = "default_normalization_pipeline"
    aggregation_strategy: str = "none"
    deprecated: bool = False
    references: tuple[MeasurementReference, ...] = ()


@dataclass(frozen=True)
class MeasurementMethod:
    name: str
    version: str
    algorithm: str
    deterministic: bool = True
    parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NormalizationMethod:
    name: str
    version: str
    source_unit: MeasurementUnit
    target_unit: MeasurementUnit
    parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MeasurementUncertainty:
    lower_bound: float
    upper_bound: float
    variance: float
    distribution: str = "bounded_interval"
    method: str = "deterministic_reliability_estimate"
    parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConfidenceBreakdown:
    source_reliability: float
    coverage: float
    agreement: float
    freshness: float
    historical_stability: float
    missing_data: float

    def value(
        self,
    ) -> float:
        return max(
            0.0,
            min(
                1.0,
                self.source_reliability
                * self.coverage
                * self.agreement
                * self.freshness
                * self.historical_stability
                * (1.0 - self.missing_data),
            ),
        )


@dataclass(frozen=True)
class MeasurementProvenance:
    source_system: str
    adapter: str
    source_event_id: str | None = None
    source_observation_id: str | None = None
    source_signal_ids: tuple[str, ...] = ()
    source_entity_ids: tuple[str, ...] = ()
    transformations: tuple[str, ...] = ()
    tenant_id: str | None = None
    target_entity: str | None = None
    target_entity_type: str | None = None
    measurement_scope: str | None = None
    raw_refs: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MeasurementTrace:
    pipeline_version: str
    dependency_ids: tuple[str, ...] = ()
    formula: str | None = None
    evaluator: str | None = None
    normalizer: str | None = None
    validator_ids: tuple[str, ...] = ()
    lineage_node_id: str | None = None


@dataclass(frozen=True)
class ValidationResult:
    status: ValidationStatus
    checks: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class Measurement:
    id: str
    definition: MeasurementDefinition
    unit: MeasurementUnit
    value: float
    confidence: float
    uncertainty: MeasurementUncertainty
    quality_score: float
    measurement_method: MeasurementMethod
    normalization_method: NormalizationMethod
    provenance: MeasurementProvenance
    timestamp: datetime
    version: str
    traceability: MeasurementTrace
    dependencies: tuple[str, ...] = ()
    validation_status: ValidationStatus = ValidationStatus.NOT_RUN
    confidence_breakdown: ConfidenceBreakdown | None = None
    calibration: Any | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SoftwareSignal:
    id: str
    name: str
    source: str
    value: Any
    unit: MeasurementUnit
    observed_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )
    source_event_id: str | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MeasurementContext:
    timestamp: datetime
    pipeline_version: str = "measurement.v1"
    tenant_id: str | None = None
    source_reliability: Mapping[str, float] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)


