"""M56 — Explanation Engine.

Converts a CausalContext into a CausalExplanation with executive-readable
narrative, ranked root causes, decomposed confidence display, and
intervention effects.
"""
from __future__ import annotations

from app.intelligence.causal.models import (
    CausalContext,
    CausalExplanation,
    CausalHypothesis,
    InterventionEffect,
    RootCause,
)


class ExplanationEngine:
    """Generates executive-readable causal explanations."""

    def generate(self, context: object, causal_ctx: "CausalContext") -> CausalExplanation:
        root_causes = causal_ctx.root_causes
        rejected = tuple(
            h for h in self._all_hypotheses(causal_ctx) if not h.accepted
        )
        intervention_effects = self._compute_intervention_effects(context, root_causes)
        summary = self._build_summary(root_causes)
        quality = self._explanation_quality(root_causes, causal_ctx)

        # Information Coverage Metric (M56.1 Enhancement)
        org = getattr(context, "org_intelligence", None)
        relevant_risks = sum(1 for r in org.knowledge_risks if r.risk_level == "HIGH") if org and hasattr(org, "knowledge_risks") else 0
        
        if not relevant_risks:
            evidence_coverage = 1.0 # If no high risks exist, coverage is perfect by default
        else:
            # How many high risks have a causal explanation?
            explained = min(len(root_causes), relevant_risks)
            
            # Weight coverage by the mean evidence confidence
            mean_conf = sum(rc.confidence.evidence_confidence for rc in root_causes) / len(root_causes) if root_causes else 0.0
            
            evidence_coverage = round((explained / relevant_risks) * mean_conf, 4)

        primary = root_causes[0] if root_causes else self._unknown_cause()
        secondary = root_causes[1:] if len(root_causes) > 1 else ()

        return CausalExplanation(
            summary=summary,
            primary_cause=primary,
            secondary_causes=secondary,
            root_cause_groups=causal_ctx.root_cause_groups,
            rejected_hypotheses=rejected,
            intervention_effects=intervention_effects,
            explanation_quality=quality,
            evidence_coverage=evidence_coverage,
        )

    # ------------------------------------------------------------------

    def _build_summary(self, root_causes: tuple[RootCause, ...]) -> str:
        if not root_causes:
            return (
                "Insufficient causal evidence to establish a definitive root cause. "
                "Ensure sufficient timeline observations and causal signals are available."
            )

        primary = root_causes[0]
        lines = [
            "Asset degradation primarily driven by:\n",
        ]
        for rc in root_causes[:3]:
            conf = rc.confidence
            lines.append(
                f"  {rc.rank}. {rc.subject:<42} "
                f"(overall conf: {conf.overall_confidence*100:.0f}%)\n"
                f"     evidence_conf: {conf.evidence_confidence*100:.0f}%  |  "
                f"rule_conf: {conf.rule_confidence*100:.0f}%  |  "
                f"propagation_conf: {conf.propagation_confidence*100:.0f}%\n"
                f"     Evidence: {rc.evidence[0].summary if rc.evidence else 'See measurements.'}\n"
            )

        if len(root_causes) > 3:
            lines.append(f"  ... and {len(root_causes) - 3} additional contributing causes.\n")

        return "".join(lines)

    def _compute_intervention_effects(
        self,
        context: object,
        root_causes: tuple[RootCause, ...],
    ) -> tuple[InterventionEffect, ...]:
        """Derive intervention effects from optimization portfolio items."""
        portfolio = None
        metrics = getattr(context, "metrics", {})
        if metrics:
            portfolio = metrics.get("optimization_portfolio")

        effects: list[InterventionEffect] = []
        if portfolio and portfolio.selected_items:
            for item in portfolio.selected_items[:3]:
                # Find root causes that the intervention addresses
                affected: list[str] = []
                for rc in root_causes:
                    if any(
                        keyword in item.action.lower()
                        for keyword in [
                            rc.subject.lower().split()[0],
                            rc.mechanism_id.split("_")[0],
                        ]
                    ):
                        affected.append(rc.causal_chain.effect_node_id)

                # Derive the expected causal mechanism explanation
                mechanism = (
                    f"Addressing {root_causes[0].subject} breaks the causal chain "
                    f"leading to bus factor collapse and health deterioration."
                    if root_causes else "Intervention reduces knowledge concentration risk."
                )

                from app.intelligence.causal.models import CausalConfidence
                effect_conf = CausalConfidence.combine(
                    evidence=0.75,
                    rule=0.80,
                    propagation=0.70,
                )
                effects.append(
                    InterventionEffect(
                        intervention_action=item.action,
                        affected_node_ids=tuple(affected[:3]),
                        expected_direction="improve",
                        expected_health_delta=item.expected_health_gain * 0.1,
                        causal_mechanism=mechanism,
                        confidence=effect_conf,
                    )
                )
        return tuple(effects)

    def _explanation_quality(
        self,
        root_causes: tuple[RootCause, ...],
        causal_ctx: "CausalContext",
    ) -> str:
        if not root_causes:
            return "FAIL"
        avg_conf = sum(rc.confidence.overall_confidence for rc in root_causes) / len(root_causes)
        if avg_conf >= 0.75 and causal_ctx.total_hypotheses_accepted >= 2:
            return "PASS"
        if avg_conf >= 0.60:
            return "PARTIAL"
        return "FAIL"

    def _all_hypotheses(self, causal_ctx: "CausalContext") -> tuple[CausalHypothesis, ...]:
        # Hypotheses are not stored directly on CausalContext in this implementation;
        # rejected ones are available via CausalExplanation.rejected_hypotheses
        return ()

    def _unknown_cause(self) -> RootCause:
        from uuid import NAMESPACE_URL, uuid5
        from app.intelligence.causal.models import CausalChain, CausalConfidence
        conf = CausalConfidence.combine(0.0, 0.0, 0.0)
        chain = CausalChain(
            root_cause_ids=(),
            effect_node_id="unknown",
            edges=(),
            overall_confidence=conf,
        )
        return RootCause(
            id=str(uuid5(NAMESPACE_URL, "root_cause|unknown")),
            subject="Unknown",
            mechanism_id="health_reduction",
            mechanism_category="Organizational",
            confidence=conf,
            evidence=(),
            rank=1,
            causal_chain=chain,
        )
