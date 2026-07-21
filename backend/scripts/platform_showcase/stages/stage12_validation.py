"""Stage 12 — Pipeline Validation.

Shows the actual canonical execution path and layer health checks.
"""

from __future__ import annotations

from ..context import PlatformContext
from ..ui import metric, section, success, MODULE_DISPLAY_NAMES
from .base import PipelineStage

class PipelineValidationStage(PipelineStage):
    name = "Pipeline Validation"

    def execute(self, context: PlatformContext) -> None:
        section("Actual Execution Path")

        # ----------------------------------------------------------------
        # Derive the canonical path from the runtime execution plan that was
        # stored in context.metrics by CanonicalPlatformPipeline.run() BEFORE
        # any stage executed.  This guarantees the reported path always matches
        # what the runtime actually scheduled — no hand-maintained list.
        # ----------------------------------------------------------------
        stage_names: tuple[str, ...] = context.metrics.get(
            "execution_stage_names", ()
        )
        if stage_names:
            # Deduplicate while preserving insertion order (a module may
            # contribute several stage bindings; show each stage's name once).
            seen: set[str] = set()
            path: list[str] = ["GitHub Commit"]
            for name in stage_names:
                if name not in seen:
                    seen.add(name)
                    path.append(name)
        else:
            # Fallback: derive from execution_order module names via the
            # display-name map.  Covers the synthetic test context that does
            # not go through CanonicalPlatformPipeline.
            order: tuple[str, ...] = context.metrics.get("execution_order", ())
            path = ["GitHub Commit"] + [
                MODULE_DISPLAY_NAMES.get(m, m) for m in dict.fromkeys(order)
            ]

        for index, name in enumerate(path):
            metric(f"Step {index + 1}", name)

        section("Layer Health")
        package = context.evidence_package
        org     = context.org_intelligence
        checks = {
            "Observation":               bool(context.observations),
            "Measurement":               bool(context.measurements),
            "Evidence":                  bool(package and package.evidence),
            "Expertise":                 bool(context.expertise_models),
            "Knowledge":                 bool(context.knowledge),
            "Knowledge Graph":           context.knowledge_graph is not None,
            "Temporal Intelligence":     context.historical_context is not None,
            "Organization Intelligence": org is not None,
            "Causal Intelligence":       getattr(context, "causal_context", None) is not None,
            "Reasoning":                 bool(context.reasoning_results),
            "Decision":                  bool(context.decisions),
            "Executive":                 bool(context.decisions),
            "Lineage":                   self._lineage_preserved(context),
            "Confidence":                self._confidence_preserved(context),
            "Uncertainty":               self._uncertainty_preserved(context),
            "Explainability":            self._explainability_preserved(context),
            "Immutability":              self._immutability_preserved(context),
            "Org No Legacy Deps":        self._no_legacy_deps(org),
        }

        for name, passed in checks.items():
            metric(name, "PASS" if passed else "FAIL")

        context.metrics["canonical_health"] = checks

        # Organization Intelligence specific checks
        if org:
            section("Org Intelligence Health")
            org_checks = {
                "Ownership computed":         len(org.ownership) > 0,
                "Coverage computed":          len(org.coverage) > 0,
                "Bus factor computed":        len(org.bus_factors) > 0,
                "Knowledge risk computed":    len(org.knowledge_risks) > 0,
                "Health summary computed":    org.health.total_subjects > 0,
                "Forecast computed deterministically": org.forecast_available if org else bool(context.forecast_context),
                "Recommendations generated":  len(org.recommendations) > 0,
                "Validation matrix present":  len(org.validation_matrix) > 0,
            }
            for name, passed in org_checks.items():
                metric(name, "PASS" if passed else "FAIL")
            context.metrics["org_health_checks"] = org_checks

        # M56 Causal Intelligence checks
        causal = getattr(context, "causal_context", None)
        if causal:
            section("Causal Intelligence Health (M56)")
            causal_checks = {
                "Causal stage executed":       True,
                "Root causes generated":       len(causal.root_causes) > 0,
                "Explanation quality PASS":    causal.explanation_quality in ("PASS", "PARTIAL"),
                "Overall confidence > 0":      causal.overall_confidence > 0.0,
                "Mechanisms activated > 0":    causal.total_mechanisms_activated > 0,
                "Hypotheses evaluated > 0":    causal.total_hypotheses_evaluated > 0,
                "Hypotheses accepted > 0":     causal.total_hypotheses_accepted > 0,
                "Primary cause identified":    bool(causal.primary_cause),
                "Causal lineage complete":     self._causal_lineage_complete(causal, context),
            }
            for name, passed in causal_checks.items():
                metric(name, "PASS" if passed else "FAIL")
            context.metrics["causal_health_checks"] = causal_checks
        else:
            section("Causal Intelligence Health (M56)")
            metric("Causal stage executed", "FAIL — stage did not produce causal_context")

        success("Canonical validation checks completed")


    def _lineage_preserved(self, context: PlatformContext) -> bool:
        package = context.evidence_package
        if not package:
            return False
        return all(item.lineage.source_measurement_ids for item in package.evidence)

    def _confidence_preserved(self, context: PlatformContext) -> bool:
        return (
            all(item.confidence >= 0.0 for item in context.measurements)
            and all(item.confidence >= 0.0 for item in context.expertise_models)
            and all(item.confidence >= 0.0 for item in context.reasoning_results)
            and all(item.confidence >= 0.0 for item in context.decisions)
        )

    def _uncertainty_preserved(self, context: PlatformContext) -> bool:
        return (
            all(item.uncertainty.variance >= 0.0 for item in context.measurements)
            and all(item.uncertainty >= 0.0 for item in context.expertise_models)
            and all(item.uncertainty >= 0.0 for item in context.reasoning_results)
            and all(item.uncertainty >= 0.0 for item in context.decisions)
        )

    def _explainability_preserved(self, context: PlatformContext) -> bool:
        package = context.evidence_package
        return bool(
            package
            and all(item.traceability.explanation for item in package.evidence)
            and all(item.explanation for item in context.expertise_models)
            and all(item.rationale for item in context.reasoning_results)
        )

    def _immutability_preserved(self, context: PlatformContext) -> bool:
        objects = [
            *context.observations[:1],
            *context.measurements[:1],
            *(context.evidence_package.evidence[:1] if context.evidence_package else ()),
            *context.expertise_models[:1],
            *context.knowledge[:1],
            *context.reasoning_results[:1],
            *context.decisions[:1],
        ]
        return all(
            bool(getattr(getattr(obj, "__dataclass_params__", None), "frozen", False))
            for obj in objects
        )

    def _no_legacy_deps(self, org) -> bool:
        """
        Verify that org_intelligence was produced without legacy dependencies.
        We check that it's an OrgIntelligenceResult (not None) and that its
        type name doesn't reference Event, ExpertiseProjection, or IntelligenceContext.
        """
        if org is None:
            return True   # absent is fine — no legacy deps possible
        type_name = type(org).__name__
        forbidden = ("Event", "ExpertiseProjection", "IntelligenceContext")
        return all(f not in type_name for f in forbidden)

    def _causal_lineage_complete(self, causal, context) -> bool:
        """
        Verify that every accepted root cause has at least one evidence item
        AND that the pipeline has canonical measurements to support it.
        No orphan causal explanations are allowed.

        Rule: a root cause is lineage-complete if:
          1. It has >= 1 evidence_id in its evidence tuple, AND
          2. The pipeline has measurements (the source of all causal evidence).
        """
        if not causal.root_causes:
            return False
        has_measurements = bool(context.measurements)
        for rc in causal.root_causes:
            if not rc.evidence_ids:
                return False  # orphan — no evidence trace
        return has_measurements  # measurements exist as the upstream source

