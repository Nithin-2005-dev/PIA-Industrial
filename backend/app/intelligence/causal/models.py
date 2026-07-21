"""M56 — Causal Intelligence models.

All types are immutable. Causal semantics are layered on top of the
existing Knowledge Graph via the CausalSemanticModel rather than
stored in a parallel graph structure.
"""
from __future__ import annotations

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Ontology primitives (defined here, registered in ontology.py)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CausalMechanism:
    """An explicitly named causal mechanism with category and parent linkage.

    Categories: Structural | Behavioral | Documentation | Process | Organizational
    """

    id: str
    name: str
    category: str
    parent_mechanism: str | None
    description: str


# ---------------------------------------------------------------------------
# Confidence decomposition
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CausalConfidence:
    """Decomposed confidence for a causal claim.

    Keeping these separate gives much better explainability than a single
    scalar—reviewers can see exactly which component is weak.
    """

    evidence_confidence: float    # how well evidence supports the causal claim
    rule_confidence: float        # baseline confidence of the triggered rule
    propagation_confidence: float # confidence after propagation through the chain
    overall_confidence: float     # weighted composite

    @staticmethod
    def combine(
        evidence: float,
        rule: float,
        propagation: float,
    ) -> "CausalConfidence":
        overall = evidence * 0.4 + rule * 0.3 + propagation * 0.3
        return CausalConfidence(
            evidence_confidence=round(evidence, 4),
            rule_confidence=round(rule, 4),
            propagation_confidence=round(propagation, 4),
            overall_confidence=round(overall, 4),
        )


@dataclass(frozen=True, slots=True)
class CausalUncertainty:
    value: float
    source: str  # "evidence" | "rule" | "propagation"


# ---------------------------------------------------------------------------
# Causal Semantic Model (not "CausalOverlay" — it semantically augments the KG)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CausalAnnotation:
    """A causal label attached to an existing KG entity.

    References a CausalMechanism by ID so the annotation is ontology-linked
    and queryable by mechanism category from day one.
    """

    kg_entity_id: str
    mechanism_id: str   # foreign key into CausalOntology
    role: str           # "cause" | "effect" | "mediator"
    observation_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CausalNode:
    """An observable causal variable derived from pipeline outputs."""

    id: str
    name: str           # e.g. "bus_factor", "review_diversity", "health"
    observed_value: float
    direction: str      # "increasing" | "decreasing" | "stable"
    mechanism_id: str   # links to CausalOntology


@dataclass(frozen=True, slots=True)
class CausalEdge:
    """A directed causal link between two CausalNodes.

    mechanism_id is ontology-linked so edges are categorisable.
    """

    cause_node_id: str
    effect_node_id: str
    mechanism_id: str
    confidence: CausalConfidence
    direction: str   # "increase" | "decrease"
    weight: float    # strength of causal influence [0, 1]


@dataclass(frozen=True, slots=True)
class CausalSemanticModel:
    """Semantic augmentation layer over the existing Knowledge Graph.

    Does NOT duplicate graph structure. Stores causal annotations keyed
    by existing KG entity IDs, plus directed causal edges derived from
    activated rules.
    """

    annotations: tuple[CausalAnnotation, ...]
    nodes: tuple[CausalNode, ...]
    edges: tuple[CausalEdge, ...]

    def nodes_by_mechanism(self, mechanism_id: str) -> tuple[CausalNode, ...]:
        return tuple(n for n in self.nodes if n.mechanism_id == mechanism_id)

    def edges_from(self, node_id: str) -> tuple[CausalEdge, ...]:
        return tuple(e for e in self.edges if e.cause_node_id == node_id)

    def edges_to(self, node_id: str) -> tuple[CausalEdge, ...]:
        return tuple(e for e in self.edges if e.effect_node_id == node_id)


# ---------------------------------------------------------------------------
# Causal Chain — branching DAG (not a linear list)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CausalChain:
    """Branching DAG of causal steps from root causes to observed effect.

    Multiple causes can contribute to the same effect (convergent causation),
    and one cause can propagate to multiple effects — hence a DAG, not a list.
    """

    root_cause_ids: tuple[str, ...]      # CausalNode IDs at the chain root
    effect_node_id: str                  # terminal observed effect node
    edges: tuple[CausalEdge, ...]        # all edges in this sub-DAG
    overall_confidence: CausalConfidence


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CausalEvidence:
    """A pointer to canonical pipeline evidence that supports a causal claim."""

    evidence_id: str
    source: str   # "observation" | "measurement" | "expertise" | "forecast" | "simulation"
    summary: str
    weight: float  # [0, 1] — contribution to evidence_confidence


# ---------------------------------------------------------------------------
# Hypothesis and Root Cause
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CausalHypothesis:
    """A candidate causal explanation awaiting evidence scoring."""

    id: str
    cause_node_id: str
    effect_node_id: str
    mechanism_id: str
    evidence: tuple[CausalEvidence, ...]
    raw_confidence: float
    accepted: bool
    rejection_reason: str | None


@dataclass(frozen=True, slots=True)
class RootCause:
    """A confirmed root cause after hypothesis evaluation."""

    id: str
    subject: str              # human-readable name (e.g. "Ownership Concentration")
    mechanism_id: str         # ontology reference
    mechanism_category: str   # resolved from ontology
    confidence: CausalConfidence
    evidence: tuple[CausalEvidence, ...]
    rank: int                 # 1 = primary cause
    causal_chain: CausalChain


@dataclass(frozen=True, slots=True)
class RootCauseGroup:
    """Root causes that share a common causal pathway or mechanism category."""

    category: str             # "Structural" | "Behavioral" | etc.
    causes: tuple[RootCause, ...]
    combined_confidence: float


# ---------------------------------------------------------------------------
# Intervention Effect
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class InterventionEffect:
    """Predicted causal effect of one optimization intervention."""

    intervention_action: str
    affected_node_ids: tuple[str, ...]
    expected_direction: str          # "improve" | "worsen" | "neutral"
    expected_health_delta: float
    causal_mechanism: str            # human-readable explanation
    confidence: CausalConfidence


# ---------------------------------------------------------------------------
# Explanation
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CausalExplanation:
    """Executive-readable causal explanation with full traceability."""

    summary: str
    primary_cause: RootCause
    secondary_causes: tuple[RootCause, ...]
    root_cause_groups: tuple[RootCauseGroup, ...]
    rejected_hypotheses: tuple[CausalHypothesis, ...]
    intervention_effects: tuple[InterventionEffect, ...]
    explanation_quality: str   # "PASS" | "PARTIAL" | "FAIL"
    evidence_coverage: float   # fraction of org intel signals with causal evidence


# ---------------------------------------------------------------------------
# Top-level context (stored in PlatformContext.causal_context)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CausalContext:
    """Complete causal intelligence result. Read-only — never mutates pipeline state."""

    semantic_model: CausalSemanticModel
    root_causes: tuple[RootCause, ...]
    root_cause_groups: tuple[RootCauseGroup, ...]
    explanation: CausalExplanation
    overall_confidence: float
    overall_uncertainty: float
    total_mechanisms_activated: int
    total_hypotheses_evaluated: int
    total_hypotheses_accepted: int
