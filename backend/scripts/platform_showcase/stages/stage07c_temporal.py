"""
===============================================================================

Stage 07c: Temporal Intelligence

===============================================================================

Computes temporal intelligence by analyzing the current execution against
historical snapshots. Injects the HistoricalContext into the pipeline
for downstream consumption by Intelligence, Reasoning, and Executive.

===============================================================================
"""

from __future__ import annotations

from .base import PipelineStage
from ..context import PlatformContext
from ..ui import metric
from ..ui import section
from ..ui import success


class TemporalIntelligenceStage(PipelineStage):
    name = "Temporal Intelligence"

    def execute(
        self,
        context: PlatformContext,
    ) -> None:
        from app.temporal.temporal_engine import TemporalEngine

        engine = context.resolve(TemporalEngine)

        # Build full historical context (loads history, computes deltas/trends)
        historical = engine.build_historical_context(context)

        # Inject into pipeline
        context.historical_context = historical

        # -------------------------------------------------------------
        # Console output
        # -------------------------------------------------------------

        section("Historical Snapshots")

        if not historical.has_history:
            metric("Previous Snapshots", 0)
            metric("Current Snapshot", "pending")
            metric("History", "Initial baseline established")
            metric("Forecast", "unavailable until next execution")

            section("Kinematic Analysis")
            metric("State", "available")
            metric("Delta", "N/A")
            metric("Velocity", "N/A")
            metric("Acceleration", "N/A")
            metric("Momentum", "N/A")

            success("Temporal intelligence initialized")
            return

        metric("Total snapshots", historical.snapshot_count)
        metric("Current version", historical.current_version)

        section("Kinematic Analysis")
        delta = historical.delta
        if delta:
            metric("State", "available")
            metric("Delta", "computed")
            metric("Velocity", "computed")
            metric("Acceleration", "computed")
            metric("Momentum", "computed")
            
            section("Temporal Delta")
            metric("Time elapsed", f"{delta.time_elapsed_seconds:.1f} seconds")
            metric("Expertise delta", f"{delta.expertise_delta:+d}")
            metric("Knowledge delta", f"{delta.knowledge_delta:+d}")
            metric("Graph node delta", f"{delta.graph_node_delta:+d}")
            if delta.health_delta is not None:
                metric("Health delta", f"{delta.health_delta:+.2f}")

        section("Knowledge Evolution")
        for summary in historical.expertise_evolution:
            print(f"  - {summary}")
        for summary in historical.knowledge_evolution:
            print(f"  - {summary}")

        if historical.graph_diff:
            section("Structural Diff")
            metric("Nodes added", historical.graph_diff.nodes_added)
            metric("Nodes removed", historical.graph_diff.nodes_removed)
            metric("Edges added", historical.graph_diff.edges_added)
            metric("Edges removed", historical.graph_diff.edges_removed)

        section("Trend Analysis")
        for trend in historical.trends:
            # Only show non-zero velocity metrics to avoid clutter
            if abs(trend.velocity) > 0:
                metric(
                    f"Trend: {trend.metric_name}",
                    f"{trend.direction} (v={trend.velocity:+.2f}, a={trend.acceleration:+.2f}, p={trend.momentum:+.2f})"
                )

        success("Temporal intelligence computed")
