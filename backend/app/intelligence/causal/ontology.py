"""M56 — Causal Ontology.

Explicitly models causal mechanism categories and inheritance relationships.
Future milestones can reason over categories of causes (Structural, Behavioral,
Documentation, Process, Organizational) without touching the rule engine.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.intelligence.causal.models import CausalMechanism


@dataclass(frozen=True)
class CausalOntology:
    """Registry of CausalMechanism entries with ancestor traversal."""

    mechanisms: tuple[CausalMechanism, ...]

    def _by_id(self) -> dict[str, CausalMechanism]:
        return {m.id: m for m in self.mechanisms}

    def get(self, mechanism_id: str) -> CausalMechanism | None:
        return self._by_id().get(mechanism_id)

    def parent_of(self, mechanism_id: str) -> CausalMechanism | None:
        m = self._by_id().get(mechanism_id)
        if m and m.parent_mechanism:
            return self._by_id().get(m.parent_mechanism)
        return None

    def category_of(self, mechanism_id: str) -> str:
        m = self._by_id().get(mechanism_id)
        return m.category if m else "Unknown"

    def ancestors(self, mechanism_id: str) -> tuple[CausalMechanism, ...]:
        result = []
        current_id: str | None = mechanism_id
        by_id = self._by_id()
        visited: set[str] = set()
        while current_id:
            if current_id in visited:
                break
            visited.add(current_id)
            m = by_id.get(current_id)
            if not m:
                break
            result.append(m)
            current_id = m.parent_mechanism
        return tuple(result)

    def mechanisms_in_category(self, category: str) -> tuple[CausalMechanism, ...]:
        return tuple(m for m in self.mechanisms if m.category == category)

    def all_categories(self) -> tuple[str, ...]:
        return tuple(sorted({m.category for m in self.mechanisms}))


def default_causal_ontology() -> CausalOntology:
    """Returns the built-in causal ontology for M56.

    5 categories, ~15 mechanisms, with parent linkage.

    Ontology hierarchy:
      knowledge_concentration (Structural)
        └── ownership_concentration (Structural)
        └── expertise_concentration (Structural)
      bus_factor_reduction (Structural)  <- caused by knowledge_concentration
      health_reduction (Organizational)  <- caused by bus_factor_reduction
      review_diversity_decline (Behavioral)
        └── knowledge_distribution_decline (Behavioral)
            └── succession_readiness_decline (Organizational)
      documentation_decline (Documentation)
        └── knowledge_retention_decline (Documentation)
      commit_velocity_decline (Process)
        └── coverage_decline (Process)
      engineering_risk_increase (Organizational)
    """
    return CausalOntology(
        mechanisms=(
            # ── Structural ────────────────────────────────────────────────
            CausalMechanism(
                id="knowledge_concentration",
                name="Knowledge Concentration",
                category="Structural",
                parent_mechanism=None,
                description=(
                    "Knowledge about a subsystem is held by a very small number "
                    "of contributors, creating structural fragility."
                ),
            ),
            CausalMechanism(
                id="ownership_concentration",
                name="Ownership Concentration",
                category="Structural",
                parent_mechanism="knowledge_concentration",
                description=(
                    "Review and commit ownership is concentrated in one or two "
                    "contributors, a specialisation of knowledge concentration."
                ),
            ),
            CausalMechanism(
                id="expertise_concentration",
                name="Expertise Concentration",
                category="Structural",
                parent_mechanism="knowledge_concentration",
                description=(
                    "Deep technical expertise exists in only one contributor, "
                    "making the subsystem highly bus-factor-sensitive."
                ),
            ),
            CausalMechanism(
                id="bus_factor_reduction",
                name="Bus Factor Reduction",
                category="Structural",
                parent_mechanism=None,
                description=(
                    "The number of contributors whose absence would critically "
                    "impair a subsystem has fallen to one or fewer."
                ),
            ),
            # ── Behavioral ───────────────────────────────────────────────
            CausalMechanism(
                id="review_diversity_decline",
                name="Review Diversity Decline",
                category="Behavioral",
                parent_mechanism=None,
                description=(
                    "The pool of unique reviewers approving changes has shrunk, "
                    "reducing knowledge distribution through the review process."
                ),
            ),
            CausalMechanism(
                id="knowledge_distribution_decline",
                name="Knowledge Distribution Decline",
                category="Behavioral",
                parent_mechanism="review_diversity_decline",
                description=(
                    "Knowledge is spreading to fewer contributors over time, "
                    "a downstream effect of reduced review diversity."
                ),
            ),
            # ── Documentation ────────────────────────────────────────────
            CausalMechanism(
                id="documentation_decline",
                name="Documentation Activity Decline",
                category="Documentation",
                parent_mechanism=None,
                description=(
                    "Documentation commits, wiki updates, and inline comment "
                    "activity have declined, reducing knowledge capture."
                ),
            ),
            CausalMechanism(
                id="knowledge_retention_decline",
                name="Knowledge Retention Decline",
                category="Documentation",
                parent_mechanism="documentation_decline",
                description=(
                    "Institutional knowledge is being lost due to insufficient "
                    "documentation, a downstream effect of documentation decline."
                ),
            ),
            # ── Process ──────────────────────────────────────────────────
            CausalMechanism(
                id="commit_velocity_decline",
                name="Commit Velocity Decline",
                category="Process",
                parent_mechanism=None,
                description=(
                    "The rate of commits to a subsystem has fallen, indicating "
                    "reduced active maintenance or contributor disengagement."
                ),
            ),
            CausalMechanism(
                id="coverage_decline",
                name="Knowledge Coverage Decline",
                category="Process",
                parent_mechanism="commit_velocity_decline",
                description=(
                    "Coverage of a subsystem by knowledgeable contributors has "
                    "decreased, a downstream effect of reduced commit velocity."
                ),
            ),
            # ── Organizational ────────────────────────────────────────────
            CausalMechanism(
                id="succession_readiness_decline",
                name="Succession Readiness Decline",
                category="Organizational",
                parent_mechanism="knowledge_distribution_decline",
                description=(
                    "The ability of the organization to replace a key contributor "
                    "has diminished due to insufficient knowledge transfer."
                ),
            ),
            CausalMechanism(
                id="health_reduction",
                name="Organizational Health Reduction",
                category="Organizational",
                parent_mechanism=None,
                description=(
                    "The composite organizational health score has declined, "
                    "driven by upstream structural, behavioral, or process causes."
                ),
            ),
            CausalMechanism(
                id="engineering_risk_increase",
                name="Engineering Risk Increase",
                category="Organizational",
                parent_mechanism=None,
                description=(
                    "Engineering-level risk (deployment risk, regression risk, "
                    "knowledge loss risk) has increased."
                ),
            ),
            CausalMechanism(
                id="forecast_risk_increase",
                name="Forecast Risk Increase",
                category="Organizational",
                parent_mechanism="engineering_risk_increase",
                description=(
                    "Forward-looking risk indicators (bus factor trajectory, "
                    "coverage trend) show worsening projections."
                ),
            ),
            CausalMechanism(
                id="knowledge_risk_increase",
                name="Knowledge Risk Increase",
                category="Organizational",
                parent_mechanism="engineering_risk_increase",
                description=(
                    "The risk of irreversible knowledge loss due to contributor "
                    "departure or disengagement has increased."
                ),
            ),
        )
    )
