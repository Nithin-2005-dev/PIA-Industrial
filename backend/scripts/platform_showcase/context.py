"""Shared runtime state for the canonical PIA showcase."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from app.temporal.models import HistoricalContext
    from app.forecast.models import ForecastContext
    from app.simulation.models import SimulationContext


# ---------------------------------------------------------------------------
# Canonical pipeline objects (produced by each layer)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ExpertiseModel:
    id: str
    subject: str
    category: str
    score: float
    confidence: float
    uncertainty: float
    quality: float
    evidence_ids: tuple[str, ...]
    explanation: str


@dataclass(frozen=True, slots=True)
class KnowledgeModel:
    id: str
    entity_type: str
    topic: str
    expertise_count: int
    average_score: float
    average_confidence: float
    average_uncertainty: float
    summary: str


@dataclass(frozen=True, slots=True)
class ReasoningResult:
    id: str
    subject: str
    conclusion: str
    confidence: float
    uncertainty: float
    rationale: str
    knowledge_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Decision:
    id: str
    title: str
    action: str
    priority: str
    confidence: float
    uncertainty: float
    reasoning_ids: tuple[str, ...]


@dataclass(slots=True)
class StageTiming:
    name: str
    started_at: float = 0.0
    finished_at: float = 0.0
    duration: float = 0.0


# ---------------------------------------------------------------------------
# Organization Intelligence result objects
# Produced by stage08 — consumed by stage09 (Reasoning), stage11 (Executive),
# and stage13 (Summary).  Nothing here imports Event or ExpertiseProjection.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class OwnershipEntry:
    """Ownership proportion of one subject within its category group."""
    subject: str
    category: str
    ownership_percentage: float
    ownership_level: str       # PRIMARY / SECONDARY / CONTRIBUTOR
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CoverageEntry:
    """Coverage assessment for one knowledge topic / module."""
    subject: str
    category: str
    expert_count: int
    coverage_score: float
    coverage_level: str        # STRONG / MODERATE / WEAK


@dataclass(frozen=True, slots=True)
class ConcentrationEntry:
    """Knowledge concentration risk for one topic / module."""
    subject: str
    category: str
    concentration_score: float
    risk_level: str            # HIGH / MEDIUM / LOW


@dataclass(frozen=True, slots=True)
class BusFactorEntry:
    """Bus-factor metric for one topic / module."""
    subject: str
    category: str
    bus_factor: int
    coverage: float
    contributors: int
    ownership_concentration: float
    confidence: float


@dataclass(frozen=True, slots=True)
class SuccessorEntry:
    """Successor candidate within one category group."""
    primary_subject: str
    successor_subject: str
    category: str
    readiness_score: float


@dataclass(frozen=True, slots=True)
class KnowledgeRiskEntry:
    """Knowledge risk assessment for one topic / module."""
    subject: str
    category: str
    risk_level: str            # HIGH / MEDIUM / LOW
    bus_factor: int
    owner_count: int
    summary: str


@dataclass(frozen=True, slots=True)
class OrgHealthSummary:
    """Aggregated organisational health across all topics."""
    average_health: float
    best_health: float
    worst_health: float
    healthy_count: int
    warning_count: int
    critical_count: int
    total_subjects: int


@dataclass(frozen=True, slots=True)
class RecommendationEntry:
    """One actionable recommendation derived from decisions + org analysis."""
    action_type: str           # organizational / engineering / executive
    subject: str
    action: str
    priority: str
    rationale: str
    confidence: float


@dataclass(frozen=True, slots=True)
class ValidationMatrixEntry:
    """Legacy vs canonical comparison for one analytics domain."""
    domain: str
    legacy_available: bool
    canonical_available: bool
    match_quality: str         # EXACT / CLOSE / DIVERGED / UNAVAILABLE
    notes: str


@dataclass(frozen=True, slots=True)
class CausalRootCause:
    """Summary of one confirmed root cause — stored in PlatformContext."""
    subject: str
    mechanism: str
    mechanism_category: str
    evidence_confidence: float
    rule_confidence: float
    propagation_confidence: float
    overall_confidence: float
    evidence_ids: tuple[str, ...]
    rank: int


@dataclass(frozen=True, slots=True)
class CausalContextSummary:
    """Top-level causal intelligence result stored in PlatformContext."""
    root_causes: tuple[CausalRootCause, ...]
    primary_cause: str
    explanation: str
    overall_confidence: float
    overall_uncertainty: float
    rejected_hypotheses: tuple[str, ...]   # rejection reason strings
    intervention_effects: tuple[str, ...]  # human-readable effect descriptions
    explanation_quality: str               # "PASS" | "PARTIAL" | "FAIL"
    total_mechanisms_activated: int
    total_hypotheses_evaluated: int
    total_hypotheses_accepted: int


@dataclass(frozen=True, slots=True)
class OrgIntelligenceResult:
    """
    Complete organizational intelligence report produced by stage08.

    Consumed by:
      - Reasoning (stage09): enriches rationale with org signals
      - Executive Dashboard (stage11): surfaces health + risk numbers
      - Summary (stage13): final org intelligence totals
    """
    ownership: tuple[OwnershipEntry, ...]
    coverage: tuple[CoverageEntry, ...]
    concentration: tuple[ConcentrationEntry, ...]
    bus_factors: tuple[BusFactorEntry, ...]
    successors: tuple[SuccessorEntry, ...]
    knowledge_risks: tuple[KnowledgeRiskEntry, ...]
    health: OrgHealthSummary
    forecast_available: bool
    forecast_note: str
    recommendations: tuple[RecommendationEntry, ...]
    validation_matrix: tuple[ValidationMatrixEntry, ...]
    # (service_name, adapter_status) — "Adapter" or "Native"
    native_rewrite_list: tuple[tuple[str, str], ...]


# ---------------------------------------------------------------------------
# Platform context — shared mutable state threaded through all stages
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class PlatformContext:
    repository: str
    branch: str
    commit_limit: int
    github_token: str | None
    tenant_id: str
    output_directory: Path
    since_commit: str | None = None

    # Pipeline layers — populated in order
    observations: list[Any] = field(default_factory=list)
    measurements: list[Any] = field(default_factory=list)
    evidence_package: Any | None = None
    expertise_models: list[ExpertiseModel] = field(default_factory=list)
    knowledge: list[KnowledgeModel] = field(default_factory=list)
    knowledge_graph: Any | None = None
    historical_context: HistoricalContext | None = None
    forecast_context: ForecastContext | None = None
    simulation_context: SimulationContext | None = None
    org_intelligence: OrgIntelligenceResult | None = None
    causal_context: CausalContextSummary | None = None
    reasoning_graph: Any | None = None
    reasoning_results: list[ReasoningResult] = field(default_factory=list)
    decisions: list[Decision] = field(default_factory=list)

    metrics: dict[str, Any] = field(default_factory=dict)
    timings: dict[str, StageTiming] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    runtime: Any | None = None
    service_provider: Any | None = None

    def resolve(
        self,
        service,
    ):
        if self.service_provider is None:
            raise RuntimeError("Platform Runtime service provider is not attached")
        return self.service_provider.resolve(service)

    def stage(self, name: str) -> StageTiming:
        if name not in self.timings:
            self.timings[name] = StageTiming(name=name)
        return self.timings[name]

    @property
    def total_duration(self) -> float:
        return sum(s.duration for s in self.timings.values())
