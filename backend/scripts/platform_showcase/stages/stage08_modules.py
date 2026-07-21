"""Stage 08 - produce decisions from reasoning results."""

from __future__ import annotations

from uuid import NAMESPACE_URL, uuid5

from ..context import Decision, PlatformContext
from ..ui import metric, ranking, section, success, warning
from .base import PipelineStage


class DecisionStage(PipelineStage):
    name = "Reasoning to Decision"

    def execute(self, context: PlatformContext) -> None:
        reasoning_results = context.reasoning_results
        if not reasoning_results:
            warning("No reasoning results available")
            return

        decisions = []
        for result in reasoning_results:
            if "high-confidence" in result.conclusion:
                priority = "high"
                action = f"Assign active mitigation owner for {result.subject}."
            elif "moderate" in result.conclusion:
                priority = "medium"
                action = f"Schedule targeted review for {result.subject}."
            else:
                priority = "low"
                action = f"Monitor {result.subject} as more evidence arrives."

            decisions.append(
                Decision(
                    id=str(uuid5(NAMESPACE_URL, f"decision|{result.id}|{priority}")),
                    title=f"{result.subject.title()} Decision",
                    action=action,
                    priority=priority,
                    confidence=result.confidence,
                    uncertainty=result.uncertainty,
                    reasoning_ids=(result.id,),
                )
            )

        priority_rank = {"high": 3, "medium": 2, "low": 1}
        decisions.sort(
            key=lambda item: (priority_rank[item.priority], item.confidence),
            reverse=True,
        )
        context.decisions = decisions
        context.metrics["decisions"] = len(decisions)

        section("Decisions")
        metric("Decisions Produced", len(decisions))
        metric(
            "Confidence Propagated",
            "PASS" if all(item.confidence >= 0.0 for item in decisions) else "FAIL",
        )
        metric(
            "Uncertainty Propagated",
            "PASS" if all(item.uncertainty >= 0.0 for item in decisions) else "FAIL",
        )
        ranking(
            "Decision Queue",
            [
                (
                    f"{item.priority:<8} {item.title:<28} "
                    f"confidence={item.confidence:.3f}"
                )
                for item in decisions
            ],
        )
        success("Decision layer produced canonical decisions")
