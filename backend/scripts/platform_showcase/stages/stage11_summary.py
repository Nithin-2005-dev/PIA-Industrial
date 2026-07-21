"""Stage 11 - canonical executive intelligence report."""

from __future__ import annotations

from ..context import PlatformContext
from ..ui import metric, ranking, section, success
from .base import PipelineStage


class SummaryStage(PipelineStage):
    name = "Executive Intelligence Report"

    def execute(self, context: PlatformContext) -> None:
        package = context.evidence_package
        health = context.metrics.get("canonical_health", {})

        section("Executive Intelligence Report")
        metric("Repository", context.repository)
        metric("Branch", context.branch)
        metric("Observations", len(context.observations))
        metric("Measurements", len(context.measurements))
        metric("Evidence", len(package.evidence) if package else 0)
        metric("Evidence for Expertise", len(package.for_expertise()) if package else 0)
        metric("Expertise Models", len(context.expertise_models))
        metric("Knowledge Models", len(context.knowledge))
        metric("Reasoning Results", len(context.reasoning_results))
        metric("Decisions", len(context.decisions))
        metric(
            "Canonical Health",
            "PASS" if health and all(health.values()) else "FAIL",
        )

        ranking(
            "Recommended Decisions",
            [
                (
                    f"{decision.priority:<8} {decision.action} "
                    f"(confidence={decision.confidence:.3f})"
                )
                for decision in context.decisions
            ],
        )

        section("Execution Timings")
        for name, timing in context.timings.items():
            metric(name, f"{timing.duration:.3f}s")

        success("Canonical showcase completed")
