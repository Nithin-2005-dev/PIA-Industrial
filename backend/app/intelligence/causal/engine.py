"""M56 — Causal Engine (top-level orchestrator).

Calls: CausalSemanticModelBuilder → CausalRuleEngine → CausalHypothesisEngine
       → ExplanationEngine → CausalContext
"""
from __future__ import annotations

from app.intelligence.causal.explanation import ExplanationEngine
from app.intelligence.causal.graph import CausalSemanticModelBuilder
from app.intelligence.causal.hypothesis import CausalHypothesisEngine
from app.intelligence.causal.models import CausalContext
from app.intelligence.causal.ontology import CausalOntology
from app.intelligence.causal.rules import CausalRuleEngine, CausalRuleRegistry


class CausalEngine:
    """Orchestrates all causal intelligence sub-components.

    Returns a CausalContext that is read-only and never mutates pipeline state.
    """

    def __init__(
        self,
        ontology: CausalOntology,
        rule_registry: CausalRuleRegistry,
    ) -> None:
        self._ontology = ontology
        self._rule_engine = CausalRuleEngine(rule_registry)
        self._model_builder = CausalSemanticModelBuilder(self._rule_engine, ontology)
        self._hypothesis_engine = CausalHypothesisEngine(ontology)
        self._explanation_engine = ExplanationEngine()

    def analyze(self, context: object) -> CausalContext:
        """Run the full causal analysis pipeline and return a CausalContext."""

        # 1. Build the CausalSemanticModel from observable pipeline outputs
        semantic_model = self._model_builder.build(context)

        # 2. Evaluate hypotheses and discover root causes
        root_causes, all_hypotheses, root_cause_groups = self._hypothesis_engine.evaluate(
            semantic_model, context
        )

        # 3. Generate executive-readable explanation
        accepted_count = sum(1 for h in all_hypotheses if h.accepted)
        
        # Build a temporary context-like object so ExplanationEngine can read it
        temp_ctx = CausalContext(
            semantic_model=semantic_model,
            root_causes=root_causes,
            root_cause_groups=root_cause_groups,
            explanation=_placeholder_explanation(),  # placeholder; overwritten below
            overall_confidence=_avg_confidence(root_causes),
            overall_uncertainty=1.0 - _avg_confidence(root_causes),
            total_mechanisms_activated=len(semantic_model.edges),
            total_hypotheses_evaluated=len(all_hypotheses),
            total_hypotheses_accepted=accepted_count,
        )
        explanation = self._explanation_engine.generate(context, temp_ctx)

        # 4. Attach rejected hypotheses to explanation
        rejected = tuple(h for h in all_hypotheses if not h.accepted)
        from dataclasses import replace as dc_replace
        explanation = dc_replace(explanation, rejected_hypotheses=rejected)

        return CausalContext(
            semantic_model=semantic_model,
            root_causes=root_causes,
            root_cause_groups=root_cause_groups,
            explanation=explanation,
            overall_confidence=_avg_confidence(root_causes),
            overall_uncertainty=round(1.0 - _avg_confidence(root_causes), 4),
            total_mechanisms_activated=len(semantic_model.edges),
            total_hypotheses_evaluated=len(all_hypotheses),
            total_hypotheses_accepted=accepted_count,
        )


def _avg_confidence(root_causes: tuple) -> float:
    if not root_causes:
        return 0.0
    return round(
        sum(rc.confidence.overall_confidence for rc in root_causes) / len(root_causes),
        4,
    )


def _placeholder_explanation():
    """Temporary placeholder used during the two-pass construction."""
    from app.intelligence.causal.models import (
        CausalChain, CausalConfidence, CausalExplanation, RootCause
    )
    from uuid import NAMESPACE_URL, uuid5
    conf = CausalConfidence.combine(0.0, 0.0, 0.0)
    chain = CausalChain(root_cause_ids=(), effect_node_id="", edges=(), overall_confidence=conf)
    dummy_rc = RootCause(
        id=str(uuid5(NAMESPACE_URL, "placeholder")),
        subject="Unknown", mechanism_id="health_reduction",
        mechanism_category="Organizational", confidence=conf,
        evidence=(), rank=1, causal_chain=chain,
    )
    return CausalExplanation(
        summary="", primary_cause=dummy_rc, secondary_causes=(),
        root_cause_groups=(), rejected_hypotheses=(),
        intervention_effects=(), explanation_quality="FAIL",
        evidence_coverage=0.0,
    )
