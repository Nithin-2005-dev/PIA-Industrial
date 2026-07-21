"""Stage 10 - show actual canonical execution path and layer checks."""

from __future__ import annotations

from ..context import PlatformContext
from ..ui import metric, section, success
from .base import PipelineStage


class PipelineOrchestratorStage(PipelineStage):
    name = "Pipeline Orchestrator"

    def execute(self, context: PlatformContext) -> None:
        section("Actual Execution Path")
        path = [
            "GitHub Commit",
            "Observation",
            "Measurement",
            "Evidence",
            "Expertise",
            "Knowledge",
            "Reasoning",
            "Decision",
            "Executive Summary",
        ]
        for index, name in enumerate(path):
            metric(f"Step {index + 1}", name)

        section("Layer Health")
        package = context.evidence_package
        checks = {
            "Observation": bool(context.observations),
            "Measurement": bool(context.measurements),
            "Evidence": bool(package and package.evidence),
            "Expertise": bool(context.expertise_models),
            "Knowledge": bool(context.knowledge),
            "Reasoning": bool(context.reasoning_results),
            "Decision": bool(context.decisions),
            "Executive": bool(context.decisions),
            "Lineage": self._lineage_preserved(context),
            "Confidence": self._confidence_preserved(context),
            "Uncertainty": self._uncertainty_preserved(context),
            "Explainability": self._explainability_preserved(context),
            "Immutability": self._immutability_preserved(context),
        }

        for name, passed in checks.items():
            metric(name, "PASS" if passed else "FAIL")

        context.metrics["canonical_health"] = checks
        success("Canonical orchestrator checks completed")

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
            bool(getattr(getattr(item, "__dataclass_params__", None), "frozen", False))
            for item in objects
        )
