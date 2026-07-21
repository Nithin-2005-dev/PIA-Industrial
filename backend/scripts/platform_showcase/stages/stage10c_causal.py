"""Stage 10c — Causal Intelligence.

Positioned after Organization Intelligence and before Reasoning.
Reads org_intelligence, forecast_context, historical_context, and
simulation_context to build the CausalSemanticModel, discover root
causes, and generate executive-readable explanations.
"""
from __future__ import annotations

from app.causal.engine import CausalEngine
from app.causal.models import CausalContext, RootCause
from app.causal.ontology import CausalOntology
from app.causal.rules import default_rule_registry

from ..context import CausalContextSummary, CausalRootCause, PlatformContext
from ..ui import metric, ranking, section, success, warning
from .base import PipelineStage


class CausalIntelligenceStage(PipelineStage):
    """Stage 10c — Causal Intelligence & Root Cause Analysis."""

    name = "Causal Intelligence"

    def execute(self, context: PlatformContext) -> None:
        if not context.org_intelligence:
            warning("No Organization Intelligence available — skipping Causal Intelligence")
            return

        section("Causal Intelligence Engine")

        # Resolve the ontology from DI if available, otherwise use default
        try:
            ontology = context.resolve(CausalOntology)
        except Exception:
            from app.causal.ontology import default_causal_ontology
            ontology = default_causal_ontology()

        registry = default_rule_registry()
        engine = CausalEngine(ontology=ontology, rule_registry=registry)

        causal_ctx: CausalContext = engine.analyze(context)

        # Map rich CausalContext → lightweight CausalContextSummary for PlatformContext
        root_cause_summaries = tuple(
            CausalRootCause(
                subject=rc.subject,
                mechanism=rc.mechanism_id,
                mechanism_category=rc.mechanism_category,
                evidence_confidence=rc.confidence.evidence_confidence,
                rule_confidence=rc.confidence.rule_confidence,
                propagation_confidence=rc.confidence.propagation_confidence,
                overall_confidence=rc.confidence.overall_confidence,
                evidence_ids=tuple(e.evidence_id for e in rc.evidence),
                rank=rc.rank,
            )
            for rc in causal_ctx.root_causes
        )

        rejected_descriptions = tuple(
            h.rejection_reason or "rejected"
            for h in causal_ctx.explanation.rejected_hypotheses
        )

        effect_descriptions = tuple(
            f"{ie.intervention_action[:50]} → {ie.expected_direction} "
            f"(Δhealth={ie.expected_health_delta:+.2f}, conf={ie.confidence.overall_confidence:.0%})"
            for ie in causal_ctx.explanation.intervention_effects
        )

        context.causal_context = CausalContextSummary(
            root_causes=root_cause_summaries,
            primary_cause=causal_ctx.explanation.primary_cause.subject,
            explanation=causal_ctx.explanation.summary,
            overall_confidence=causal_ctx.overall_confidence,
            overall_uncertainty=causal_ctx.overall_uncertainty,
            rejected_hypotheses=rejected_descriptions,
            intervention_effects=effect_descriptions,
            explanation_quality=causal_ctx.explanation.explanation_quality,
            total_mechanisms_activated=causal_ctx.total_mechanisms_activated,
            total_hypotheses_evaluated=causal_ctx.total_hypotheses_evaluated,
            total_hypotheses_accepted=causal_ctx.total_hypotheses_accepted,
        )
        context.metrics["causal_root_causes"] = len(root_cause_summaries)

        # ── Display ────────────────────────────────────────────────────
        metric("Mechanisms Activated",      causal_ctx.total_mechanisms_activated)
        metric("Hypotheses Evaluated",      causal_ctx.total_hypotheses_evaluated)
        metric("Hypotheses Accepted",       causal_ctx.total_hypotheses_accepted)
        metric("Root Causes Identified",    len(root_cause_summaries))
        metric("Primary Cause",             context.causal_context.primary_cause)
        metric("Overall Confidence",        f"{causal_ctx.overall_confidence*100:.1f}%")
        metric("Overall Uncertainty",       f"{causal_ctx.overall_uncertainty*100:.1f}%")
        metric("Explanation Quality",       causal_ctx.explanation.explanation_quality)
        metric("Evidence Coverage",         f"{causal_ctx.explanation.evidence_coverage*100:.1f}%")

        if root_cause_summaries:
            section("Root Cause Analysis")
            print(causal_ctx.explanation.summary)

            ranking(
                "Root Causes (ranked by overall confidence)",
                [
                    (
                        f"[{rc.rank}] {rc.subject:<38} "
                        f"overall={rc.overall_confidence*100:.0f}%  "
                        f"evidence={rc.evidence_confidence*100:.0f}%  "
                        f"rule={rc.rule_confidence*100:.0f}%  "
                        f"propagation={rc.propagation_confidence*100:.0f}%  "
                        f"[{rc.mechanism_category}]"
                    )
                    for rc in root_cause_summaries
                ],
            )

        if causal_ctx.root_cause_groups:
            section("Root Cause Groups (by Mechanism Category)")
            for group in causal_ctx.root_cause_groups:
                print(
                    f"  {group.category:<20} "
                    f"{len(group.causes)} cause(s)  "
                    f"combined_conf={group.combined_confidence*100:.0f}%"
                )

        if causal_ctx.explanation.intervention_effects:
            section("Causal Intervention Effects")
            for ie in causal_ctx.explanation.intervention_effects:
                print(
                    f"  ▶ {ie.intervention_action[:60]}\n"
                    f"    → {ie.expected_direction.upper()}  "
                    f"Δhealth={ie.expected_health_delta:+.3f}  "
                    f"mechanism: {ie.causal_mechanism[:70]}\n"
                    f"    confidence: overall={ie.confidence.overall_confidence:.0%}  "
                    f"evidence={ie.confidence.evidence_confidence:.0%}  "
                    f"rule={ie.confidence.rule_confidence:.0%}\n"
                )

        if rejected_descriptions:
            section("Alternative Hypotheses (Rejected)")
            for reason in rejected_descriptions[:5]:
                print(f"  ✗ {reason}")

        success("Causal Intelligence completed — root causes identified and explained")
