"""Stage 13 — Executive Intelligence Report (Summary)."""

from __future__ import annotations

from ..context import PlatformContext
from ..ui import metric, ranking, section, success
from .base import PipelineStage


class SummaryStage(PipelineStage):
    name = "Executive Intelligence Report"

    def execute(self, context: PlatformContext) -> None:
        package = context.evidence_package
        health  = context.metrics.get("canonical_health", {})
        org     = context.org_intelligence

        section("Executive Intelligence Report")

        # Pipeline layer counts
        metric("Repository",         context.repository)
        metric("Branch",             context.branch)
        metric("Observations",       len(context.observations))
        metric("Measurements",       len(context.measurements))
        metric("Evidence",           len(package.evidence) if package else 0)
        metric("Evidence for Expertise", len(package.for_expertise()) if package else 0)
        metric("Expertise Models",   len(context.expertise_models))
        metric("Knowledge Models",   len(context.knowledge))
        sim_context = getattr(context, "simulation_context", None)
        metric("Simulation Scenarios", len(sim_context.scenarios) if sim_context else 0)
        metric("Reasoning Results",  len(context.reasoning_results))
        metric("Decisions",          len(context.decisions))
        metric(
            "Canonical Health",
            "PASS" if health and all(health.values()) else "PARTIAL" if health else "FAIL",
        )

        # Organization intelligence summary
        if org:
            section("Organization Intelligence Totals")
            metric("Ownership Entries",   len(org.ownership))
            metric("Coverage Entries",    len(org.coverage))
            metric("Concentration Entries", len(org.concentration))
            metric("Bus Factor Entries",  len(org.bus_factors))
            metric("Successor Pairs",     len(org.successors))
            metric("Knowledge Risks",     len(org.knowledge_risks))
            metric("Health (average)",    f"{org.health.average_health:.3f}")
            metric("Healthy Topics",      org.health.healthy_count)
            metric("Warning Topics",      org.health.warning_count)
            metric("Critical Topics",     org.health.critical_count)
            fc = context.forecast_context
            if fc and fc.metrics:
                metric("Forecast",            f"Computed ({len(fc.metrics)} metrics)")
            else:
                metric("Forecast",            "UNAVAILABLE (pending history)")
            metric("Recommendations",     len(org.recommendations))

            # Validation matrix pass / fail summary
            exact   = sum(1 for v in org.validation_matrix if v.match_quality == "EXACT")
            close   = sum(1 for v in org.validation_matrix if v.match_quality == "CLOSE")
            unavail = sum(1 for v in org.validation_matrix if v.match_quality == "UNAVAILABLE")
            metric("Validation Matrix — EXACT match",       exact)
            metric("Validation Matrix — CLOSE match",       close)
            metric("Validation Matrix — UNAVAILABLE",       unavail)

        ranking(
            "Recommended Decisions",
            [
                (
                    f"{d.priority:<8} {d.action:<60} "
                    f"(confidence={d.confidence:.3f})"
                )
                for d in context.decisions
            ],
        )

        if org and org.recommendations:
            ranking(
                "Top Organizational Recommendations",
                [
                    f"[{r.action_type.upper():<14}] [{r.priority.upper():<6}] {r.action[:70]}"
                    for r in org.recommendations[:8]
                ],
            )

        section("Execution Timings")
        for name, timing in context.timings.items():
            metric(name, f"{timing.duration:.3f}s")

        # Increment 5: Snapshot persistence for temporal intelligence
        import json
        from datetime import datetime
        
        snapshot_dir = context.output_directory / "history"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_file = snapshot_dir / f"snapshot_{timestamp}.json"
        
        snapshot_data = {
            "timestamp": timestamp,
            "metrics": {
                "repository": context.repository,
                "measurements": len(context.measurements),
                "evidence": len(package.evidence) if package else 0,
                "expertise_models": len(context.expertise_models),
                "knowledge_models": len(context.knowledge),
                "decisions": len(context.decisions),
            },
            "org_intelligence": {
                "health": org.health.average_health if org else 0.0,
                "critical_topics": org.health.critical_count if org else 0,
            } if org else {}
        }
        
        with open(snapshot_file, "w", encoding="utf-8") as f:
            json.dump(snapshot_data, f, indent=2)
            
        success(f"Snapshot persisted to {snapshot_file.name}")
        success("Canonical showcase completed")
