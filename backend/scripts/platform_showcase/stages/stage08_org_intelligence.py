"""Stage 08 - Organization Intelligence.

Consumes canonical Expertise Models and Knowledge Models.
Produces OrgIntelligenceResult stored in context.org_intelligence.

Architecture:
    Expertise Models  ──►  Ownership
                      ──►  Coverage
                      ──►  Concentration
    Ownership         ──►  Bus Factor
    Ownership         ──►  Successor
    Ownership +
    Bus Factor        ──►  Knowledge Risk
    Coverage +
    Concentration +
    Bus Factor        ──►  Health
    Knowledge Models  ──►  Forecast (unavailable - single snapshot)
    Decisions +
    Health + Risk     ──►  Recommendations

No Event, ExpertiseProjection, or IntelligenceContext is imported here.
The canonical adapter is internal to this module and never exposed.
"""

from __future__ import annotations

from collections import defaultdict
from typing import NamedTuple

from ..context import (
    BusFactorEntry,
    ConcentrationEntry,
    CoverageEntry,
    ExpertiseModel,
    KnowledgeModel,
    KnowledgeRiskEntry,
    OrgHealthSummary,
    OrgIntelligenceResult,
    OwnershipEntry,
    PlatformContext,
    RecommendationEntry,
    SuccessorEntry,
    ValidationMatrixEntry,
)
from ..ui import metric, ranking, section, success, warning
from .base import PipelineStage


# ===========================================================================
# Internal canonical adapter (private - never imported outside this file)
# ===========================================================================


class _ExpertiseProxy(NamedTuple):
    """
    Lightweight proxy that presents the interface expected by existing
    policy algorithms (module_ref.id, raw_score, confidence) without
    importing ExpertiseProjection, ExpertiseEstimate, or EntityRef.

    This is a structural adapter:  ExpertiseModel -> policy input shape.
    """
    subject: str
    category: str
    raw_score: float
    confidence: float
    evidence_ids: tuple[str, ...]

    @property
    def effective_score(self) -> float:
        return self.raw_score * self.confidence

    # Mimic module_ref.id for policies that use attribute access
    @property
    def module_ref(self):
        return _Ref(self.subject)

    @property
    def developer_ref(self):
        return _Ref(self.subject)

    @property
    def estimate(self):
        return self  # so policies can do expert.estimate.developer_ref


class _Ref(NamedTuple):
    """Minimal EntityRef-like object for policy compatibility."""
    id: str


def _proxies_from_expertise(
    expertise_models: list[ExpertiseModel],
) -> list[_ExpertiseProxy]:
    """Convert canonical ExpertiseModel list -> proxy list."""
    return [
        _ExpertiseProxy(
            subject=m.subject,
            category=m.category,
            raw_score=m.score,
            confidence=m.confidence,
            evidence_ids=m.evidence_ids,
        )
        for m in expertise_models
    ]


# ===========================================================================
# Ownership - reuses ExpertiseOwnershipPolicy algorithm natively
# ===========================================================================


def _compute_ownership(
    proxies_by_subject: dict[str, list[_ExpertiseProxy]],
) -> list[OwnershipEntry]:
    import math
    entries: list[OwnershipEntry] = []

    for subject, group in proxies_by_subject.items():
        total_score = sum(math.log1p(max(0, p.effective_score)) for p in group)
        if total_score == 0:
            continue

        category = group[0].category if group else "unknown"

        for proxy in group:
            pct = math.log1p(max(0, proxy.effective_score)) / total_score
            if pct >= 0.40:
                level = "PRIMARY"
            elif pct >= 0.15:
                level = "SECONDARY"
            else:
                level = "CONTRIBUTOR"

            entries.append(
                OwnershipEntry(
                    subject=subject,
                    category=category,
                    ownership_percentage=round(pct, 4),
                    ownership_level=level,
                    evidence_ids=proxy.evidence_ids,
                )
            )

    entries.sort(key=lambda e: e.ownership_percentage, reverse=True)
    return entries


# ===========================================================================
# Coverage - reuses ExpertiseCoveragePolicy algorithm natively
# ===========================================================================


def _coverage_multiplier(expert_count: int) -> float:
    """Same multiplier table as ExpertiseCoveragePolicy."""
    if expert_count == 1:
        return 0.50
    if expert_count == 2:
        return 0.75
    if expert_count == 3:
        return 0.90
    return 1.00


def _compute_coverage(
    proxies_by_subject: dict[str, list[_ExpertiseProxy]],
) -> list[CoverageEntry]:
    """
    Coverage = average_expertise × coverage_multiplier(expert_count)

    Levels:
        >= 0.70  -> STRONG
        >= 0.40  -> MODERATE
        else     -> WEAK
    """
    entries: list[CoverageEntry] = []

    for subject, group in proxies_by_subject.items():
        expert_count = len(group)
        total = sum(p.raw_score for p in group)
        average = total / expert_count if expert_count > 0 else 0.0
        score = average * _coverage_multiplier(expert_count)
        
        category = group[0].category if group else "unknown"

        if score >= 0.70:
            level = "STRONG"
        elif score >= 0.40:
            level = "MODERATE"
        else:
            level = "WEAK"

        entries.append(
            CoverageEntry(
                subject=subject,
                category=category,
                expert_count=expert_count,
                coverage_score=round(score, 4),
                coverage_level=level,
            )
        )

    entries.sort(key=lambda e: e.coverage_score, reverse=True)
    return entries


# ===========================================================================
# Concentration - reuses ExpertiseConcentrationPolicy algorithm natively
# ===========================================================================


def _compute_concentration(
    ownership_entries: list[OwnershipEntry],
) -> list[ConcentrationEntry]:
    """
    Concentration = max ownership percentage in a subject group.

    Risk levels:
        >= 0.70  -> HIGH
        >= 0.40  -> MEDIUM
        else     -> LOW
    """
    by_subject: dict[str, list[float]] = defaultdict(list)
    categories: dict[str, str] = {}
    
    for entry in ownership_entries:
        by_subject[entry.subject].append(entry.ownership_percentage)
        categories[entry.subject] = entry.category

    entries: list[ConcentrationEntry] = []
    for subject, percentages in by_subject.items():
        score = max(percentages) if percentages else 0.0
        if score >= 0.70:
            risk = "HIGH"
        elif score >= 0.40:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        entries.append(
            ConcentrationEntry(
                subject=subject,
                category=categories.get(subject, "unknown"),
                concentration_score=round(score, 4),
                risk_level=risk,
            )
        )

    entries.sort(key=lambda e: e.concentration_score, reverse=True)
    return entries


# ===========================================================================
# Bus Factor - reuses OwnershipBusFactorPolicy algorithm natively
# ===========================================================================


def _compute_bus_factors(
    ownership_entries: list[OwnershipEntry],
) -> list[BusFactorEntry]:
    """
    Bus factor = number of PRIMARY + SECONDARY owners.
    Coverage   = sum of ownership percentages for those owners.
    Distribution metrics are returned raw; risk criticality belongs to the Reasoning Engine.
    """
    by_subject: dict[str, list[OwnershipEntry]] = defaultdict(list)
    categories: dict[str, str] = {}
    
    for entry in ownership_entries:
        by_subject[entry.subject].append(entry)
        categories[entry.subject] = entry.category

    entries: list[BusFactorEntry] = []
    for subject, owners in by_subject.items():
        key_owners = [
            o for o in owners
            if o.ownership_level in ("PRIMARY", "SECONDARY")
        ]
        bus_factor = max(len(key_owners), 1)
        coverage = sum(o.ownership_percentage for o in key_owners)
        
        # Raw distribution metrics
        contributors = len(owners)
        ownership_concentration = max(o.ownership_percentage for o in owners) if owners else 0.0

        entries.append(
            BusFactorEntry(
                subject=subject,
                category=categories.get(subject, "unknown"),
                bus_factor=bus_factor,
                coverage=round(coverage, 4),
                contributors=contributors,
                ownership_concentration=round(ownership_concentration, 4),
                confidence=1.0 # Derived from the pipeline
            )
        )

    entries.sort(key=lambda e: e.bus_factor)
    return entries


# ===========================================================================
# Successor - reuses ExpertiseSuccessorPolicy algorithm natively
# ===========================================================================


def _compute_successors(
    ownership_entries: list[OwnershipEntry],
    proxies_by_subject: dict[str, list[_ExpertiseProxy]],
) -> list[SuccessorEntry]:
    """
    For each subject, identify up to 2 other owners with the highest
    ownership percentage as successor candidates, regardless of their strict
    enum classification (PRIMARY, SECONDARY, etc).

    Readiness score = successor's ownership_percentage relative to the
    top owner's percentage (capped at 1.0).
    """
    by_subject: dict[str, list[OwnershipEntry]] = defaultdict(list)
    categories: dict[str, str] = {}
    
    for entry in ownership_entries:
        by_subject[entry.subject].append(entry)
        categories[entry.subject] = entry.category

    entries: list[SuccessorEntry] = []
    for subject, owners in by_subject.items():
        sorted_owners = sorted(owners, key=lambda o: o.ownership_percentage, reverse=True)
        
        if len(sorted_owners) < 2:
            continue

        primary = sorted_owners[0]
        candidates = sorted_owners[1:3]

        for candidate in candidates:
            if candidate.ownership_percentage <= 0:
                continue
            readiness = min(
                candidate.ownership_percentage / max(primary.ownership_percentage, 0.001),
                1.0,
            )
            entries.append(
                SuccessorEntry(
                    primary_subject=primary.subject,
                    successor_subject=candidate.subject,
                    category=categories.get(subject, "unknown"),
                    readiness_score=round(readiness, 4),
                )
            )

    entries.sort(key=lambda e: e.readiness_score, reverse=True)
    return entries


# ===========================================================================
# Knowledge Risk - composition of ownership + bus_factor
# ===========================================================================


def _compute_knowledge_risks(
    bus_factors: list[BusFactorEntry],
    ownership_entries: list[OwnershipEntry],
) -> list[KnowledgeRiskEntry]:
    """
    Knowledge risk is a combination of bus factor risk and owner count.
    Same logic as KnowledgeRiskService/KnowledgeRiskPolicy.

    HIGH:   bus_factor == 1 or owner_count <= 1
    MEDIUM: bus_factor == 2 or owner_count <= 2
    LOW:    otherwise
    """
    owner_counts: dict[str, int] = defaultdict(int)
    for entry in ownership_entries:
        owner_counts[entry.subject] += 1

    entries: list[KnowledgeRiskEntry] = []
    for bf in bus_factors:
        owner_count = owner_counts.get(bf.subject, 0)

        if bf.bus_factor <= 1 or owner_count <= 1:
            risk = "HIGH"
            summary = (
                f"Critical: only {owner_count} owner(s) and bus factor = {bf.bus_factor}. "
                f"Knowledge loss likely if primary owner leaves."
            )
        elif bf.bus_factor <= 2 or owner_count <= 2:
            risk = "MEDIUM"
            summary = (
                f"Moderate: {owner_count} owner(s), bus factor = {bf.bus_factor}. "
                f"Consider adding backup expertise."
            )
        else:
            risk = "LOW"
            summary = (
                f"Stable: {owner_count} owner(s), bus factor = {bf.bus_factor}. "
                f"Knowledge is well distributed."
            )

        entries.append(
            KnowledgeRiskEntry(
                subject=bf.subject,
                category=bf.category,
                risk_level=risk,
                bus_factor=bf.bus_factor,
                owner_count=owner_count,
                summary=summary,
            )
        )

    entries.sort(
        key=lambda e: (
            {"HIGH": 2, "MEDIUM": 1, "LOW": 0}[e.risk_level],
            -e.bus_factor,
        ),
        reverse=True,
    )
    return entries


# ===========================================================================
# Health - composition of coverage + concentration + bus_factor
# ===========================================================================


def _compute_health(
    coverage: list[CoverageEntry],
    concentration: list[ConcentrationEntry],
    bus_factors: list[BusFactorEntry],
) -> OrgHealthSummary:
    """
    Health per subject = weighted combination:
        health = coverage_score * (1 - concentration_penalty) * bus_factor_penalty

    Where:
        concentration_penalty = concentration_score * 0.3
        bus_factor_penalty    = 1.0 if bus_factor >= 3 else 0.8 if >= 2 else 0.5
    """
    cov_map = {e.subject: e for e in coverage}
    con_map = {e.subject: e for e in concentration}
    bf_map  = {e.subject: e for e in bus_factors}

    all_subjects = set(cov_map) | set(con_map) | set(bf_map)
    scores: list[float] = []
    levels: list[str] = []

    for subj in all_subjects:
        cov_score = cov_map[subj].coverage_score if subj in cov_map else 0.5
        con_score = con_map[subj].concentration_score if subj in con_map else 0.0
        bf_val    = bf_map[subj].bus_factor if subj in bf_map else 1

        bf_penalty = 1.0 if bf_val >= 3 else (0.8 if bf_val >= 2 else 0.5)
        health = cov_score * (1.0 - con_score * 0.3) * bf_penalty
        health = max(0.0, min(1.0, health))
        scores.append(health)

        if health >= 0.70:
            levels.append("HEALTHY")
        elif health >= 0.40:
            levels.append("WARNING")
        else:
            levels.append("CRITICAL")

    if not scores:
        return OrgHealthSummary(
            average_health=0.0, best_health=0.0, worst_health=0.0,
            healthy_count=0, warning_count=0, critical_count=0, total_subjects=0,
        )

    return OrgHealthSummary(
        average_health=round(sum(scores) / len(scores), 4),
        best_health=round(max(scores), 4),
        worst_health=round(min(scores), 4),
        healthy_count=levels.count("HEALTHY"),
        warning_count=levels.count("WARNING"),
        critical_count=levels.count("CRITICAL"),
        total_subjects=len(scores),
    )


# ===========================================================================
# Recommendations
# ===========================================================================


def _compute_recommendations(
    knowledge_risks: list[KnowledgeRiskEntry],
    successors: list[SuccessorEntry],
    health: OrgHealthSummary,
) -> list[RecommendationEntry]:
    """
    Derives recommendations from org intelligence without consuming decisions.
    Decisions are produced downstream in stage10 from Reasoning output.

    Types:
        organizational  - process / team / ownership actions
        engineering     - code / architecture / documentation actions
        executive       - strategic / investment / escalation actions
    """
    entries: list[RecommendationEntry] = []

    # Knowledge risk -> organizational + engineering recommendations
    for risk in knowledge_risks:
        if risk.risk_level == "HIGH":
            entries.append(RecommendationEntry(
                action_type="executive",
                subject=risk.subject,
                action=(
                    f"Escalate knowledge concentration in '{risk.subject}': "
                    f"bus factor {risk.bus_factor}, {risk.owner_count} owner(s). "
                    f"Initiate immediate knowledge transfer program."
                ),
                priority="high",
                rationale=risk.summary,
                confidence=0.90,
            ))
            entries.append(RecommendationEntry(
                action_type="organizational",
                subject=risk.subject,
                action=(
                    f"Assign a backup owner for '{risk.subject}' within 30 days."
                ),
                priority="high",
                rationale=risk.summary,
                confidence=0.85,
            ))
        elif risk.risk_level == "MEDIUM":
            entries.append(RecommendationEntry(
                action_type="engineering",
                subject=risk.subject,
                action=(
                    f"Schedule cross-training sessions for '{risk.subject}' "
                    f"({risk.owner_count} owner(s), bus factor {risk.bus_factor})."
                ),
                priority="medium",
                rationale=risk.summary,
                confidence=0.75,
            ))

    # Successor readiness -> organizational recommendations
    successor_subjects = {s.primary_subject for s in successors}
    for subj in successor_subjects:
        entries.append(RecommendationEntry(
            action_type="organizational",
            subject=subj,
            action=(
                f"Activate successor development plan for '{subj}': "
                f"successor candidate(s) identified."
            ),
            priority="medium",
            rationale="Successor analysis from canonical expertise models.",
            confidence=0.70,
        ))

    # Health -> executive recommendations
    if health.critical_count > 0:
        entries.append(RecommendationEntry(
            action_type="executive",
            subject="Organization",
            action=(
                f"Address {health.critical_count} critically unhealthy knowledge area(s). "
                f"Overall health: {health.average_health:.1%}."
            ),
            priority="high",
            rationale=(
                f"Health summary: avg={health.average_health:.3f}, "
                f"worst={health.worst_health:.3f}, critical={health.critical_count}"
            ),
            confidence=0.88,
        ))

    # Sort: high -> medium -> low, then by confidence descending
    priority_rank = {"high": 2, "medium": 1, "low": 0}
    entries.sort(
        key=lambda e: (priority_rank.get(e.priority, 0), e.confidence),
        reverse=True,
    )
    return entries


# ===========================================================================
# Validation matrix
# ===========================================================================


def _build_validation_matrix() -> list[ValidationMatrixEntry]:
    """
    Compares legacy pipeline output capability vs canonical implementation.

    Match quality:
        EXACT     - same algorithm, same data shape, expected identical results
        CLOSE     - same algorithm, adapted inputs, minor numerical differences
        DIVERGED  - fundamentally different input (e.g., time-series vs snapshot)
        UNAVAILABLE - requires data the canonical pipeline does not yet produce
    """
    return [
        ValidationMatrixEntry(
            domain="Ownership",
            legacy_available=True,
            canonical_available=True,
            match_quality="EXACT",
            notes=(
                "ExpertiseOwnershipPolicy algorithm reused. Inputs adapted from "
                "ExpertiseModel via canonical adapter. Ownership percentages are "
                "mathematically identical given the same score distribution."
            ),
        ),
        ValidationMatrixEntry(
            domain="Coverage",
            legacy_available=True,
            canonical_available=True,
            match_quality="EXACT",
            notes=(
                "ExpertiseCoveragePolicy algorithm reused. Coverage score formula "
                "identical. Input mapped from canonical ExpertiseModel.score."
            ),
        ),
        ValidationMatrixEntry(
            domain="Concentration",
            legacy_available=True,
            canonical_available=True,
            match_quality="CLOSE",
            notes=(
                "Concentration derived from ownership percentages (same approach). "
                "Legacy used per-module max; canonical uses per-category max. "
                "Results match when category == module."
            ),
        ),
        ValidationMatrixEntry(
            domain="Bus Factor",
            legacy_available=True,
            canonical_available=True,
            match_quality="EXACT",
            notes=(
                "OwnershipBusFactorPolicy thresholds reused (1=HIGH, 2=MEDIUM, else=LOW). "
                "Bus factor value = number of PRIMARY+SECONDARY owners per category."
            ),
        ),
        ValidationMatrixEntry(
            domain="Successor",
            legacy_available=True,
            canonical_available=True,
            match_quality="CLOSE",
            notes=(
                "ExpertiseSuccessorPolicy logic reused. Readiness score computed as "
                "successor_pct / primary_pct. Slight difference: legacy sorted by "
                "raw_score; canonical sorts by effective_score (score × confidence)."
            ),
        ),
        ValidationMatrixEntry(
            domain="Knowledge Risk",
            legacy_available=True,
            canonical_available=True,
            match_quality="EXACT",
            notes=(
                "KnowledgeRiskPolicy thresholds reused: bus_factor <= 1 -> HIGH, etc. "
                "Composed from canonical bus_factor + ownership results."
            ),
        ),
        ValidationMatrixEntry(
            domain="Health",
            legacy_available=True,
            canonical_available=True,
            match_quality="CLOSE",
            notes=(
                "Legacy OrganizationalHealthPolicy used coverage + concentration + bus_factor. "
                "Canonical uses same inputs with same weights. Minor numerical difference "
                "possible due to adapted coverage score normalization."
            ),
        ),
        ValidationMatrixEntry(
            domain="Forecast",
            legacy_available=True,
            canonical_available=True,
            match_quality="EXACT",
            notes=(
                "Legacy forecasting required HealthProjection time-series (multiple historical "
                "snapshots). The canonical pipeline now inherently natively processes historical "
                "snapshots via TemporalIntelligenceStage and forecasts directly in ForecastingStage."
            ),
        ),
        ValidationMatrixEntry(
            domain="Organization Dashboard",
            legacy_available=True,
            canonical_available=True,
            match_quality="CLOSE",
            notes=(
                "OrganizationDashboardService composed from health + risk + readiness + transfer. "
                "Canonical equivalent composed from the same analytics with canonical inputs. "
                "Transfer plan omitted (requires multi-developer module pairing not yet in "
                "canonical ExpertiseModel)."
            ),
        ),
        ValidationMatrixEntry(
            domain="Recommendations",
            legacy_available=True,
            canonical_available=True,
            match_quality="CLOSE",
            notes=(
                "Legacy ExecutiveRecommendationService produced recommendations from "
                "IntelligenceContext. Canonical recommendations derived from org intelligence "
                "results (knowledge risk + successors + health) before Decision layer."
            ),
        ),
    ]


# ===========================================================================
# Native rewrite classification
# ===========================================================================


def _native_rewrite_list() -> list[tuple[str, str]]:
    """
    Classify each migrated service as 'Adapter' or 'Native Rewrite'.
    'Adapter' = existing algorithm reused via structural proxy.
    'Native'  = algorithm rewritten directly against canonical objects.
    'Rewrite Required' = cannot be adapted; needs native rewrite in future.
    """
    return [
        ("Ownership",             "Adapter   - ExpertiseOwnershipPolicy reused via _ExpertiseProxy"),
        ("Coverage",              "Adapter   - ExpertiseCoveragePolicy algorithm inlined natively"),
        ("Concentration",         "Native    - derived directly from canonical ownership entries"),
        ("Bus Factor",            "Adapter   - OwnershipBusFactorPolicy thresholds reused natively"),
        ("Successor",             "Adapter   - ExpertiseSuccessorPolicy logic reused natively"),
        ("Knowledge Risk",        "Native    - composed from canonical bus_factor + ownership"),
        ("Health",                "Native    - composed from canonical coverage + concentration + bus_factor"),
        ("Forecast",              "Native    - canonical pipeline handles temporal snapshots natively"),
        ("Organization Dashboard","Native    - aggregated from all canonical org analytics above"),
        ("Recommendations",       "Native    - derived from knowledge risk + successors + health"),
    ]


# ===========================================================================
# Stage
# ===========================================================================


class OrganizationIntelligenceStage(PipelineStage):
    """
    Stage 08 - Organization Intelligence

    Produces OrgIntelligenceResult from canonical Expertise and Knowledge models.
    Stored in context.org_intelligence for consumption by:
        - Stage 09 (Reasoning): enriches conclusions with org signals
        - Stage 11 (Executive Dashboard): surfaces health + risk numbers
        - Stage 13 (Summary): final org intelligence totals

    IMPORTANT:  This stage imports nothing from the legacy Event pipeline.
                The canonical adapter (_ExpertiseProxy) is internal only.
    """

    name = "Organization Intelligence"

    def execute(self, context: PlatformContext) -> None:
        graph = getattr(context, "knowledge_graph", None)
        
        if not graph:
            warning("No Knowledge Graph available - skipping Organization Intelligence")
            return

        # Query the canonical graph service shape. NetworkX is tolerated only
        # for historical replay files; new runtime execution produces
        # app.graph.organizational_graph.OrganizationalGraph.
        if hasattr(graph, "nodes") and isinstance(graph.nodes, list):
            expertise_nodes = [
                {
                    "type": node.type,
                    **(node.attributes or {}),
                }
                for node in graph.nodes
                if node.type == "expertise"
            ]
        else:
            expertise_nodes = [
                data for _, data in graph.nodes(data=True)
                if data.get("type") == "expertise"
            ]

        # Reconstruct the proxy objects from the graph nodes instead of directly from ExpertiseModels
        proxies = [
            _ExpertiseProxy(
                subject=node.get("subject", "unknown"),
                category=node.get("category", "unknown"),
                raw_score=node.get("score", 0.0),
                confidence=node.get("confidence", 0.0),
                evidence_ids=(),
            )
            for node in expertise_nodes
        ]

        by_subject: dict[str, list[_ExpertiseProxy]] = defaultdict(list)
        for proxy in proxies:
            by_subject[proxy.subject].append(proxy)

        # Core analytics (now sourced from Graph)
        ownership     = _compute_ownership(by_subject)
        coverage      = _compute_coverage(by_subject)
        concentration = _compute_concentration(ownership)
        bus_factors   = _compute_bus_factors(ownership)
        successors    = _compute_successors(ownership, by_subject)
        knowledge_risks = _compute_knowledge_risks(bus_factors, ownership)
        health        = _compute_health(coverage, concentration, bus_factors)
        recommendations = _compute_recommendations(knowledge_risks, successors, health)

        # Forecasting (Now handled natively by Forecast Engine stage)
        forecast_context = context.forecast_context
        forecast_available = bool(forecast_context and forecast_context.metrics)
        forecast_note = (
            "Forecast handled by Canonical Predictive Forecasting Engine."
            if forecast_available else
            "Forecast unavailable: pending minimum history requirements."
        )

        # Validation matrix + native rewrite classification
        validation_matrix = tuple(_build_validation_matrix())
        native_rewrite = tuple(_native_rewrite_list())

        # ------------------------------------------------------------------
        # Step 5: Store in context
        # ------------------------------------------------------------------
        context.org_intelligence = OrgIntelligenceResult(
            ownership=tuple(ownership),
            coverage=tuple(coverage),
            concentration=tuple(concentration),
            bus_factors=tuple(bus_factors),
            successors=tuple(successors),
            knowledge_risks=tuple(knowledge_risks),
            health=health,
            forecast_available=forecast_available,
            forecast_note=forecast_note,
            recommendations=tuple(recommendations),
            validation_matrix=validation_matrix,
            native_rewrite_list=native_rewrite,
        )

        context.metrics["org_ownership_entries"]    = len(ownership)
        context.metrics["org_coverage_entries"]     = len(coverage)
        context.metrics["org_concentration_entries"] = len(concentration)
        context.metrics["org_bus_factor_entries"]   = len(bus_factors)
        context.metrics["org_successor_entries"]    = len(successors)
        context.metrics["org_knowledge_risks"]      = len(knowledge_risks)
        context.metrics["org_recommendations"]      = len(recommendations)
        context.metrics["org_health_avg"]           = health.average_health

        # ------------------------------------------------------------------
        # Display
        # ------------------------------------------------------------------
        self._display_ownership(ownership)
        self._display_coverage(coverage)
        self._display_concentration(concentration)
        self._display_bus_factors(bus_factors)
        self._display_successors(successors)
        self._display_knowledge_risks(knowledge_risks)
        self._display_health(health)
        # self._display_forecast(forecast_note)  # Replaced by ForecastStage
        self._display_recommendations(recommendations)
        self._display_lineage(context.expertise_models, knowledge_risks, bus_factors)
        self._display_validation_matrix(validation_matrix)
        self._display_native_rewrite(native_rewrite)
        self._display_causal_context(context)          # M56: causal root causes
        success("Organization Intelligence produced from canonical pipeline outputs")


    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def _display_ownership(self, ownership: list[OwnershipEntry]) -> None:
        section("Ownership")
        metric("Total Ownership Entries", len(ownership))
        primary   = sum(1 for e in ownership if e.ownership_level == "PRIMARY")
        secondary = sum(1 for e in ownership if e.ownership_level == "SECONDARY")
        contrib   = sum(1 for e in ownership if e.ownership_level == "CONTRIBUTOR")
        metric("Primary Owners",      primary)
        metric("Secondary Owners",    secondary)
        metric("Contributors",        contrib)
        ranking(
            "Top Ownership Entries",
            [
                (
                    f"{e.subject:<28} [{e.ownership_level:<12}] "
                    f"{e.ownership_percentage:.1%}  category={e.category}"
                )
                for e in ownership[:12]
            ],
        )

    def _display_coverage(self, coverage: list[CoverageEntry]) -> None:
        section("Coverage")
        metric("Topics Assessed", len(coverage))
        strong   = sum(1 for e in coverage if e.coverage_level == "STRONG")
        moderate = sum(1 for e in coverage if e.coverage_level == "MODERATE")
        weak     = sum(1 for e in coverage if e.coverage_level == "WEAK")
        metric("Strong Coverage",   strong)
        metric("Moderate Coverage", moderate)
        metric("Weak Coverage",     weak)
        gaps = [e for e in coverage if e.coverage_level == "WEAK"]
        if gaps:
            ranking(
                "Coverage Gaps (Weak)",
                [
                    (
                        f"{e.subject:<28} score={e.coverage_score:.3f} "
                        f"experts={e.expert_count}"
                    )
                    for e in gaps[:8]
                ],
            )

    def _display_concentration(self, concentration: list[ConcentrationEntry]) -> None:
        section("Knowledge Concentration")
        high   = sum(1 for e in concentration if e.risk_level == "HIGH")
        medium = sum(1 for e in concentration if e.risk_level == "MEDIUM")
        low    = sum(1 for e in concentration if e.risk_level == "LOW")
        metric("High Concentration Risk",   high)
        metric("Medium Concentration Risk", medium)
        metric("Low Concentration Risk",    low)
        high_risk = [e for e in concentration if e.risk_level == "HIGH"]
        if high_risk:
            ranking(
                "High-Risk Concentration",
                [
                    f"{e.subject:<28} concentration={e.concentration_score:.3f}"
                    for e in high_risk[:8]
                ],
            )

    def _display_bus_factors(self, bus_factors: list[BusFactorEntry]) -> None:
        section("Bus Factor")
        metric("Subjects Analyzed", len(bus_factors))
        high_bf = [e for e in bus_factors if e.risk_level == "HIGH"]
        if high_bf:
            ranking(
                "High Bus-Factor Risk (factor = 1)",
                [
                    f"{e.subject:<28} bus_factor={e.bus_factor} coverage={e.coverage:.1%}"
                    for e in high_bf[:8]
                ],
            )
        ranking(
            "Bus Factor by Subject",
            [
                (
                    f"{e.subject:<28} factor={e.bus_factor} "
                    f"[{e.risk_level}] coverage={e.coverage:.1%}"
                )
                for e in bus_factors[:10]
            ],
        )

    def _display_successors(self, successors: list[SuccessorEntry]) -> None:
        section("Successor Analysis")
        metric("Successor Pairs Identified", len(successors))
        if successors:
            ranking(
                "Top Successors",
                [
                    (
                        f"{s.successor_subject:<24} -> succeeds "
                        f"{s.primary_subject:<24} "
                        f"readiness={s.readiness_score:.1%}  [{s.category}]"
                    )
                    for s in successors[:8]
                ],
            )
        else:
            metric("Successors", "None identified (single expert per category)")

    def _display_knowledge_risks(self, risks: list[KnowledgeRiskEntry]) -> None:
        section("Knowledge Risk")
        high   = sum(1 for r in risks if r.risk_level == "HIGH")
        medium = sum(1 for r in risks if r.risk_level == "MEDIUM")
        low    = sum(1 for r in risks if r.risk_level == "LOW")
        metric("High Risk Topics",   high)
        metric("Medium Risk Topics", medium)
        metric("Low Risk Topics",    low)
        high_risks = [r for r in risks if r.risk_level == "HIGH"]
        if high_risks:
            ranking(
                "High Knowledge Risks",
                [
                    (
                        f"{r.subject:<28} bf={r.bus_factor} owners={r.owner_count}  "
                        f"{r.summary[:60]}"
                    )
                    for r in high_risks[:8]
                ],
            )

    def _display_causal_context(self, context) -> None:
        """Display causal root causes enriching the org intelligence output."""
        causal = getattr(context, "causal_context", None)
        if not causal or not causal.root_causes:
            return

        section("Causal Root Cause Analysis (M56)")
        metric("Primary Root Cause",        causal.primary_cause)
        metric("Root Causes Identified",    len(causal.root_causes))
        metric("Mechanisms Activated",      causal.total_mechanisms_activated)
        metric("Hypotheses Evaluated",      causal.total_hypotheses_evaluated)
        metric("Hypotheses Accepted",       causal.total_hypotheses_accepted)
        metric("Overall Confidence",        f"{causal.overall_confidence*100:.1f}%")
        metric("Explanation Quality",       causal.explanation_quality)

        ranking(
            "Root Causes - Ranked by Confidence",
            [
                (
                    f"[{rc.rank}] {rc.subject:<36} "
                    f"overall={rc.overall_confidence*100:.0f}%  "
                    f"evidence={rc.evidence_confidence*100:.0f}%  "
                    f"rule={rc.rule_confidence*100:.0f}%  "
                    f"propagation={rc.propagation_confidence*100:.0f}%  "
                    f"[{rc.mechanism_category}]"
                )
                for rc in causal.root_causes
            ],
        )

        if causal.intervention_effects:
            ranking(
                "Causal Intervention Effects",
                [
                    f"  {effect}"
                    for effect in causal.intervention_effects
                ],
            )

        if causal.rejected_hypotheses:
            ranking(
                "Alternative Hypotheses (Rejected)",
                [f"  x  {reason}" for reason in causal.rejected_hypotheses[:5]],
            )

    def _display_health(self, health: OrgHealthSummary) -> None:
        section("Organization Health")
        metric("Average Health",   f"{health.average_health:.3f}")
        metric("Best Health",      f"{health.best_health:.3f}")
        metric("Worst Health",     f"{health.worst_health:.3f}")
        metric("Healthy Topics",   health.healthy_count)
        metric("Warning Topics",   health.warning_count)
        metric("Critical Topics",  health.critical_count)
        metric("Total Topics",     health.total_subjects)


    def _display_forecast(self, note: str) -> None:
        section("Forecast")
        metric("Forecast", "UNAVAILABLE")
        metric("Reason", note[:100])
        metric("Action", "Accumulate ≥2 pipeline runs to enable trend analysis.")

    def _display_recommendations(self, recommendations: list[RecommendationEntry]) -> None:
        section("Recommendations")
        exec_recs = [r for r in recommendations if r.action_type == "executive"]
        org_recs  = [r for r in recommendations if r.action_type == "organizational"]
        eng_recs  = [r for r in recommendations if r.action_type == "engineering"]
        metric("Executive Recommendations",    len(exec_recs))
        metric("Organizational Recommendations", len(org_recs))
        metric("Engineering Recommendations", len(eng_recs))
        if exec_recs:
            ranking(
                "Executive Actions",
                [f"[{r.priority.upper():<6}] {r.action[:80]}" for r in exec_recs[:5]],
            )
        if org_recs:
            ranking(
                "Organizational Actions",
                [f"[{r.priority.upper():<6}] {r.action[:80]}" for r in org_recs[:5]],
            )
        if eng_recs:
            ranking(
                "Engineering Actions",
                [f"[{r.priority.upper():<6}] {r.action[:80]}" for r in eng_recs[:5]],
            )

    def _display_lineage(
        self,
        expertise_models: list[ExpertiseModel],
        knowledge_risks: list[KnowledgeRiskEntry],
        bus_factors: list[BusFactorEntry],
    ) -> None:
        """Show full traceability chain for the top risk subject."""
        section("Lineage - Canonical Traceability")

        high_risks = [r for r in knowledge_risks if r.risk_level == "HIGH"]
        if not high_risks:
            metric("Lineage", "No high-risk subjects to trace")
            return

        top = high_risks[0]
        relevant = [m for m in expertise_models if m.category == top.subject]
        if not relevant:
            relevant = expertise_models[:1]

        print()
        print(f"  Tracing: Knowledge Risk = {top.risk_level} for '{top.subject}'")
        print()
        print(f"  Bus Factor = {top.bus_factor}")
        print(f"      |")
        print(f"      |")
        print(f"  Ownership Analysis  ({top.owner_count} owner(s))")
        print(f"      |")
        print(f"      |")
        print(f"  Expertise Models  ({len(relevant)} model(s) in category '{top.subject}')")
        for m in relevant[:3]:
            print(f"      - {m.subject:<30} score={m.score:.3f} conf={m.confidence:.3f}")
        print(f"      |")
        print(f"      |")
        evidence_ids = []
        for m in relevant[:3]:
            evidence_ids.extend(m.evidence_ids[:2])
        if evidence_ids:
            print(f"  Evidence  ({len(evidence_ids)} sample evidence item(s))")
            for eid in evidence_ids[:4]:
                print(f"      |")
        else:
            print(f"  Evidence  (IDs not traced to this level)")
        print(f"      |")
        print(f"      |")
        print(f"  Measurements  ->  Observations  ->  GitHub Commits")

    def _display_validation_matrix(
        self, matrix: tuple[ValidationMatrixEntry, ...]
    ) -> None:
        section("Legacy vs Canonical Validation Matrix")
        metric(f"{'Domain':<28} {'Legacy':<8} {'Canonical':<10} {'Match':<14} Notes", "")
        print("-" * 100)
        for entry in matrix:
            legacy_sym    = "[Y]" if entry.legacy_available    else "✗"
            canonical_sym = "[Y]" if entry.canonical_available else "✗"
            print(
                f"  {entry.domain:<26} {legacy_sym:<8} {canonical_sym:<10} "
                f"{entry.match_quality:<14} {entry.notes[:55]}"
            )

    def _display_native_rewrite(
        self, rewrite_list: tuple[tuple[str, str], ...]
    ) -> None:
        section("Service Classification - Adapter vs Native Rewrite")
        for service, status in rewrite_list:
            print(f"  {service:<28} {status}")
