"""M56 — Causal Rule Registry.

Rules are not hardcoded inside the engine.  Each RuleProvider contributes
a set of CausalRules to the CausalRuleRegistry.  Future milestones can
register new providers without modifying the engine.

Built-in providers:
  DocumentationRuleProvider
  OwnershipRuleProvider
  ReviewRuleProvider
  ExpertiseRuleProvider
  VelocityRuleProvider
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# Rule contract
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CausalRule:
    """An immutable causal rule definition.

    cause_node / effect_node reference CausalNode.name values observed
    from pipeline context.  mechanism_id links to the CausalOntology.
    """

    id: str
    cause_node: str       # observable variable name (e.g. "documentation_activity")
    effect_node: str      # observable variable name (e.g. "knowledge_retention")
    direction: str        # "decrease" | "increase" — direction of the effect
    mechanism_id: str     # foreign key into CausalOntology
    rule_confidence: float
    description: str


# ---------------------------------------------------------------------------
# Provider protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class RuleProvider(Protocol):
    """Extensibility protocol: implement to add a new rule set."""

    @property
    def name(self) -> str: ...

    def rules(self) -> tuple[CausalRule, ...]: ...


# ---------------------------------------------------------------------------
# Built-in providers
# ---------------------------------------------------------------------------


class DocumentationRuleProvider:
    """Documentation activity → knowledge retention → bus factor → health."""

    name = "documentation"

    def rules(self) -> tuple[CausalRule, ...]:
        return (
            CausalRule(
                id="doc.knowledge_retention",
                cause_node="documentation_activity",
                effect_node="knowledge_retention",
                direction="decrease",
                mechanism_id="documentation_decline",
                rule_confidence=0.88,
                description=(
                    "When documentation activity decreases, knowledge retention "
                    "deteriorates because institutional knowledge is not captured."
                ),
            ),
            CausalRule(
                id="knowledge_retention.bus_factor",
                cause_node="knowledge_retention",
                effect_node="bus_factor",
                direction="decrease",
                mechanism_id="knowledge_retention_decline",
                rule_confidence=0.85,
                description=(
                    "When knowledge retention declines, fewer contributors can "
                    "independently maintain a subsystem, reducing bus factor."
                ),
            ),
            CausalRule(
                id="bus_factor.health",
                cause_node="bus_factor",
                effect_node="health",
                direction="decrease",
                mechanism_id="bus_factor_reduction",
                rule_confidence=0.92,
                description=(
                    "A bus factor of 1 or below directly reduces organizational "
                    "health by creating a single point of failure."
                ),
            ),
        )


class OwnershipRuleProvider:
    """Ownership concentration → knowledge risk → forecast risk → executive priority."""

    name = "ownership"

    def rules(self) -> tuple[CausalRule, ...]:
        return (
            CausalRule(
                id="ownership_concentration.knowledge_risk",
                cause_node="ownership_concentration",
                effect_node="knowledge_risk",
                direction="increase",
                mechanism_id="ownership_concentration",
                rule_confidence=0.94,
                description=(
                    "High ownership concentration in a single contributor "
                    "directly increases knowledge risk for that subsystem."
                ),
            ),
            CausalRule(
                id="knowledge_risk.forecast_risk",
                cause_node="knowledge_risk",
                effect_node="forecast_risk",
                direction="increase",
                mechanism_id="knowledge_risk_increase",
                rule_confidence=0.87,
                description=(
                    "High knowledge risk propagates into worsening forecast risk "
                    "as the probability of knowledge loss increases over time."
                ),
            ),
            CausalRule(
                id="forecast_risk.executive_priority",
                cause_node="forecast_risk",
                effect_node="executive_priority",
                direction="increase",
                mechanism_id="forecast_risk_increase",
                rule_confidence=0.82,
                description=(
                    "Elevated forecast risk triggers an increase in executive "
                    "priority for the affected subsystem."
                ),
            ),
        )


class ReviewRuleProvider:
    """Review diversity → knowledge distribution → succession readiness → engineering risk."""

    name = "review"

    def rules(self) -> tuple[CausalRule, ...]:
        return (
            CausalRule(
                id="review_diversity.knowledge_distribution",
                cause_node="review_diversity",
                effect_node="knowledge_distribution",
                direction="decrease",
                mechanism_id="review_diversity_decline",
                rule_confidence=0.86,
                description=(
                    "When fewer unique reviewers participate, knowledge is "
                    "distributed to a smaller fraction of the team."
                ),
            ),
            CausalRule(
                id="knowledge_distribution.succession_readiness",
                cause_node="knowledge_distribution",
                effect_node="succession_readiness",
                direction="decrease",
                mechanism_id="knowledge_distribution_decline",
                rule_confidence=0.83,
                description=(
                    "Poor knowledge distribution means fewer contributors can "
                    "succeed a key maintainer, reducing succession readiness."
                ),
            ),
            CausalRule(
                id="succession_readiness.engineering_risk",
                cause_node="succession_readiness",
                effect_node="engineering_risk",
                direction="increase",
                mechanism_id="succession_readiness_decline",
                rule_confidence=0.80,
                description=(
                    "Low succession readiness increases engineering risk because "
                    "any key contributor departure becomes a critical incident."
                ),
            ),
        )


class ExpertiseRuleProvider:
    """Expertise concentration → bus factor → health."""

    name = "expertise"

    def rules(self) -> tuple[CausalRule, ...]:
        return (
            CausalRule(
                id="expertise_concentration.bus_factor",
                cause_node="expertise_concentration",
                effect_node="bus_factor",
                direction="decrease",
                mechanism_id="expertise_concentration",
                rule_confidence=0.91,
                description=(
                    "When deep expertise is concentrated in a single contributor, "
                    "the effective bus factor collapses toward 1."
                ),
            ),
            CausalRule(
                id="expertise_concentration.knowledge_risk",
                cause_node="expertise_concentration",
                effect_node="knowledge_risk",
                direction="increase",
                mechanism_id="expertise_concentration",
                rule_confidence=0.89,
                description=(
                    "Concentrated expertise creates high knowledge risk because "
                    "that contributor's departure removes irreplaceable knowledge."
                ),
            ),
        )


class VelocityRuleProvider:
    """Commit velocity decline → coverage decline → health decline."""

    name = "velocity"

    def rules(self) -> tuple[CausalRule, ...]:
        return (
            CausalRule(
                id="commit_velocity.coverage",
                cause_node="commit_velocity",
                effect_node="coverage",
                direction="decrease",
                mechanism_id="commit_velocity_decline",
                rule_confidence=0.79,
                description=(
                    "Declining commit velocity signals reduced active maintenance, "
                    "which gradually erodes knowledge coverage for a subsystem."
                ),
            ),
            CausalRule(
                id="coverage.health",
                cause_node="coverage",
                effect_node="health",
                direction="decrease",
                mechanism_id="coverage_decline",
                rule_confidence=0.84,
                description=(
                    "Low knowledge coverage reduces organizational health because "
                    "fewer contributors can handle critical changes."
                ),
            ),
        )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class CausalRuleRegistry:
    """Collects CausalRules from all registered RuleProviders."""

    def __init__(self) -> None:
        self._providers: list[RuleProvider] = []

    def register(self, provider: RuleProvider) -> None:
        self._providers.append(provider)

    def all_rules(self) -> tuple[CausalRule, ...]:
        rules: list[CausalRule] = []
        for p in self._providers:
            rules.extend(p.rules())
        return tuple(rules)

    def provider_names(self) -> tuple[str, ...]:
        return tuple(p.name for p in self._providers)


def default_rule_registry() -> CausalRuleRegistry:
    """Builds the default registry with built-in providers."""
    registry = CausalRuleRegistry()
    from app.intelligence.causal.industrial_rules import IndustrialReliabilityRuleProvider
    registry.register(IndustrialReliabilityRuleProvider())
    return registry


# ---------------------------------------------------------------------------
# Rule Engine
# ---------------------------------------------------------------------------


class CausalRuleEngine:
    """Evaluates activated rules against observed node states."""

    def __init__(self, registry: CausalRuleRegistry) -> None:
        self._registry = registry

    def evaluate(
        self,
        observed_nodes: dict[str, float],
    ) -> tuple[CausalRule, ...]:
        """Return rules whose cause_node is observable and trending unfavourably."""
        activated: list[CausalRule] = []
        for rule in self._registry.all_rules():
            value = observed_nodes.get(rule.cause_node)
            if value is None:
                continue
            # For "decrease" rules: activate if value < 0.5 (weak/declining)
            # For "increase" rules: activate if value > 0.5 (elevated)
            if rule.direction == "decrease" and value < 0.5:
                activated.append(rule)
            elif rule.direction == "increase" and value > 0.5:
                activated.append(rule)
        return tuple(activated)
