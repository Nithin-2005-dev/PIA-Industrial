"""M56 — Causal Semantic Model Builder.

Constructs the CausalSemanticModel by reading existing pipeline outputs
(org_intelligence, historical_context, forecast_context, simulation_context)
and attaching causal annotations to existing KG entity IDs.

No new graph storage is created — CausalSemanticModel is a thin semantic
augmentation layer over the existing Knowledge Graph.
"""
from __future__ import annotations

from uuid import NAMESPACE_URL, uuid5

from app.intelligence.causal.models import (
    CausalAnnotation,
    CausalConfidence,
    CausalEdge,
    CausalNode,
    CausalSemanticModel,
)
from app.intelligence.causal.ontology import CausalOntology
from app.intelligence.causal.rules import CausalRule, CausalRuleEngine


def _node_id(name: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"causal_node|{name}"))


class CausalSemanticModelBuilder:
    """Derives observable causal nodes from pipeline context and constructs
    the CausalSemanticModel by activating registered rules against them."""

    def __init__(
        self,
        rule_engine: CausalRuleEngine,
        ontology: CausalOntology,
    ) -> None:
        self._rule_engine = rule_engine
        self._ontology = ontology

    def build(self, context: object) -> CausalSemanticModel:
        observed = self._observe_nodes(context)
        activated_rules = self._rule_engine.evaluate(observed)
        nodes = self._make_nodes(observed, activated_rules)
        edges = self._make_edges(nodes, activated_rules, observed)
        annotations = self._annotate_kg(context, nodes)
        return CausalSemanticModel(
            annotations=annotations,
            nodes=tuple(nodes.values()),
            edges=edges,
        )

    # ------------------------------------------------------------------
    # Observation: read pipeline context into {node_name: float} dict
    # ------------------------------------------------------------------

    def _observe_nodes(self, context: object) -> dict[str, float]:
        """Extract observable causal variable values from pipeline outputs."""
        observed: dict[str, float] = {}

        org = getattr(context, "org_intelligence", None)
        if org:
            # Bus factor: normalise so 1 → 0.0 (worst), 5+ → 1.0 (best)
            if org.bus_factors:
                avg_bf = sum(b.bus_factor for b in org.bus_factors) / len(org.bus_factors)
                observed["bus_factor"] = min(1.0, avg_bf / 5.0)

            # Ownership concentration: high score = bad → invert for "health" direction
            if org.concentration:
                avg_conc = sum(c.concentration_score for c in org.concentration) / len(org.concentration)
                observed["ownership_concentration"] = avg_conc  # 1.0 = fully concentrated (bad)

            # Coverage: average coverage score [0, 1]
            if org.coverage:
                avg_cov = sum(c.coverage_score for c in org.coverage) / len(org.coverage)
                observed["coverage"] = avg_cov

            # Health
            observed["health"] = org.health.average_health

            # Knowledge risk: fraction of topics at HIGH risk
            if org.knowledge_risks:
                high_frac = sum(1 for r in org.knowledge_risks if r.risk_level == "HIGH") / len(org.knowledge_risks)
                observed["knowledge_risk"] = high_frac
                observed["forecast_risk"] = high_frac  # proxy

            # Expertise concentration: use ownership concentration as proxy
            if "ownership_concentration" in observed:
                observed["expertise_concentration"] = observed["ownership_concentration"]

            # Succession readiness: fraction of subjects with successors identified
            if org.bus_factors:
                total = len(org.bus_factors)
                with_successor = len(org.successors)
                observed["succession_readiness"] = with_successor / total if total else 0.5

            # Review diversity: proxy from coverage
            if "coverage" in observed:
                observed["review_diversity"] = observed["coverage"]

            # Knowledge distribution: proxy from coverage
            observed["knowledge_distribution"] = observed.get("coverage", 0.5)

        hist = getattr(context, "historical_context", None)
        if hist and hist.trends:
            for trend in hist.trends:
                mn = trend.metric_name
                # velocity > 0 means growing; normalise around 0.5
                vel_norm = min(1.0, max(0.0, 0.5 + trend.velocity * 0.1))
                if "commit" in mn or "velocity" in mn:
                    observed["commit_velocity"] = vel_norm
                if "doc" in mn:
                    observed["documentation_activity"] = vel_norm

        fc = getattr(context, "forecast_context", None)
        if fc and fc.metrics:
            for mn, series in fc.metrics.items():
                f30 = series.get_forecast(30)
                if f30:
                    if "health" in mn:
                        observed["forecast_health"] = max(0.0, min(1.0, f30.predicted_value))

        # Defaults for any missing nodes (neutral 0.5)
        for key in [
            "bus_factor", "ownership_concentration", "coverage", "health",
            "knowledge_risk", "forecast_risk", "expertise_concentration",
            "succession_readiness", "review_diversity", "knowledge_distribution",
            "commit_velocity", "documentation_activity", "knowledge_retention",
            "engineering_risk", "executive_priority",
        ]:
            observed.setdefault(key, 0.5)

        return observed

    # ------------------------------------------------------------------
    # Node construction
    # ------------------------------------------------------------------

    def _make_nodes(
        self,
        observed: dict[str, float],
        activated_rules: tuple[CausalRule, ...],
    ) -> dict[str, CausalNode]:
        """Build CausalNode objects for every observed variable."""
        # Collect all node names referenced by activated rules + observed dict
        node_names: set[str] = set(observed.keys())
        for rule in activated_rules:
            node_names.add(rule.cause_node)
            node_names.add(rule.effect_node)

        nodes: dict[str, CausalNode] = {}
        for name in node_names:
            value = observed.get(name, 0.5)
            # Direction heuristic: > 0.6 = "increasing", < 0.4 = "decreasing"
            if value > 0.6:
                direction = "increasing"
            elif value < 0.4:
                direction = "decreasing"
            else:
                direction = "stable"

            # Find a mechanism ID for this node name from activated rules
            mechanism_id = "health_reduction"  # fallback
            for rule in activated_rules:
                if rule.cause_node == name or rule.effect_node == name:
                    mechanism_id = rule.mechanism_id
                    break

            nodes[name] = CausalNode(
                id=_node_id(name),
                name=name,
                observed_value=round(value, 4),
                direction=direction,
                mechanism_id=mechanism_id,
            )
        return nodes

    # ------------------------------------------------------------------
    # Edge construction
    # ------------------------------------------------------------------

    def _make_edges(
        self,
        nodes: dict[str, CausalNode],
        activated_rules: tuple[CausalRule, ...],
        observed: dict[str, float],
    ) -> tuple[CausalEdge, ...]:
        edges: list[CausalEdge] = []
        for rule in activated_rules:
            cause = nodes.get(rule.cause_node)
            effect = nodes.get(rule.effect_node)
            if not cause or not effect:
                continue

            # Evidence confidence: how far the observed value deviates from neutral
            cause_val = observed.get(rule.cause_node, 0.5)
            if rule.direction == "decrease":
                evidence_conf = round(1.0 - cause_val, 4)  # lower = stronger evidence
            else:
                evidence_conf = round(cause_val, 4)         # higher = stronger evidence

            evidence_conf = max(0.3, min(0.99, evidence_conf))
            propagation_conf = round(rule.rule_confidence * 0.95, 4)

            confidence = CausalConfidence.combine(
                evidence=evidence_conf,
                rule=rule.rule_confidence,
                propagation=propagation_conf,
            )

            edges.append(
                CausalEdge(
                    cause_node_id=cause.id,
                    effect_node_id=effect.id,
                    mechanism_id=rule.mechanism_id,
                    confidence=confidence,
                    direction=rule.direction,
                    weight=round(confidence.overall_confidence, 4),
                )
            )
        return tuple(edges)

    # ------------------------------------------------------------------
    # KG annotation
    # ------------------------------------------------------------------

    def _annotate_kg(
        self,
        context: object,
        nodes: dict[str, CausalNode],
    ) -> tuple[CausalAnnotation, ...]:
        """Attach causal annotations to existing KG entity IDs."""
        annotations: list[CausalAnnotation] = []
        kg = getattr(context, "knowledge_graph", None)
        if kg is None:
            return ()

        # Iterate KG nodes if the graph exposes them
        kg_nodes = getattr(kg, "nodes", None)
        if kg_nodes is None:
            return ()

        for kg_entity in kg_nodes:
            entity_id = getattr(kg_entity, "id", None) or str(kg_entity)
            # Heuristic: annotate nodes that match a causal node name in their label
            label = getattr(kg_entity, "label", "") or getattr(kg_entity, "name", "") or ""
            for node_name, causal_node in nodes.items():
                if node_name.replace("_", " ") in label.lower() or node_name in label.lower():
                    annotations.append(
                        CausalAnnotation(
                            kg_entity_id=entity_id,
                            mechanism_id=causal_node.mechanism_id,
                            role="cause" if causal_node.direction == "decreasing" else "effect",
                            observation_ids=(),
                        )
                    )
                    break

        return tuple(annotations)
