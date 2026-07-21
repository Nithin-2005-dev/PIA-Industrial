"""Stage 09 - executive dashboard from canonical outputs."""

from __future__ import annotations

from ..context import PlatformContext
from ..ui import lineage, metric, ranking, section, success, warning
from .base import PipelineStage


class ExecutiveDashboardStage(PipelineStage):
    name = "Executive Dashboard"

    def execute(self, context: PlatformContext) -> None:
        if not context.decisions:
            warning("No decisions available")
            return

        section("Executive Dashboard")
        package = context.evidence_package
        metric("Observations", len(context.observations))
        metric("Measurements", len(context.measurements))
        metric("Evidence", len(package.evidence) if package else 0)
        metric("Expertise Models", len(context.expertise_models))
        metric("Knowledge Models", len(context.knowledge))
        metric("Reasoning Results", len(context.reasoning_results))
        metric("Decisions", len(context.decisions))

        high_priority = sum(1 for item in context.decisions if item.priority == "high")
        medium_priority = sum(1 for item in context.decisions if item.priority == "medium")
        low_priority = sum(1 for item in context.decisions if item.priority == "low")
        metric("High Priority Decisions", high_priority)
        metric("Medium Priority Decisions", medium_priority)
        metric("Low Priority Decisions", low_priority)

        if context.decisions:
            average_confidence = sum(item.confidence for item in context.decisions) / len(context.decisions)
            average_uncertainty = sum(item.uncertainty for item in context.decisions) / len(context.decisions)
            metric("Decision Confidence", f"{average_confidence:.3f}")
            metric("Decision Uncertainty", f"{average_uncertainty:.3f}")

        ranking(
            "Executive Actions",
            [
                f"{item.priority:<8} {item.action}"
                for item in context.decisions[:10]
            ],
        )
        lineage("Canonical Lineage")
        success("Executive dashboard rendered from canonical outputs")
