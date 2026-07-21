"""Temporal Engine — core temporal intelligence computations.

This is the primary service for the ``temporal`` runtime module.
It orchestrates snapshot creation, delta computation, trend analysis
(with velocity, acceleration, and momentum), and historical context
assembly.

Snapshots are the source of truth.  Every derived view (delta, trend,
historical context) can be recomputed from the snapshot sequence.
"""

from __future__ import annotations

from datetime import datetime

from app.intelligence.temporal.graph_diff import GraphDiffEngine
from app.intelligence.temporal.models import GraphDiffResult
from app.intelligence.temporal.models import HistoricalContext
from app.intelligence.temporal.models import SnapshotVersionInfo
from app.intelligence.temporal.models import TemporalDelta
from app.intelligence.temporal.models import TemporalSnapshot
from app.intelligence.temporal.models import TemporalTrend
from app.intelligence.temporal.snapshot_repository import SnapshotRepository


# ---------------------------------------------------------------------------
# Trend direction thresholds
# ---------------------------------------------------------------------------

_STABLE_THRESHOLD = 0.001


class TemporalEngine:
    """Core temporal intelligence computations.

    Lifecycle within the canonical pipeline:

    1. ``build_historical_context()`` — called by TemporalIntelligenceStage
       to load history, compute deltas/trends, and inject context.
    2. ``create_snapshot()`` — called after all stages complete to persist
       the current execution as an immutable snapshot.
    """

    def __init__(
        self,
        repository: SnapshotRepository,
        graph_diff: GraphDiffEngine,
    ):
        self._repository = repository
        self._graph_diff = graph_diff

    @property
    def repository(self) -> SnapshotRepository:
        """Expose repository for snapshot persistence by the pipeline."""
        return self._repository

    # ------------------------------------------------------------------
    # Snapshot creation
    # ------------------------------------------------------------------

    def create_snapshot(
        self,
        context,
    ) -> TemporalSnapshot:
        """Build a TemporalSnapshot from the current PlatformContext.

        This captures the full state of the pipeline at the point of
        completion, producing an immutable record for future comparison.
        """
        package = context.evidence_package
        org = context.org_intelligence
        graph = context.knowledge_graph

        graph_node_count = 0
        graph_edge_count = 0
        if graph is not None:
            graph_node_count = len(getattr(graph, "nodes", []))
            graph_edge_count = len(getattr(graph, "edges", []))

        expertise_subjects = tuple(
            sorted(set(m.subject for m in context.expertise_models))
        )
        knowledge_topics = tuple(
            sorted(set(k.topic for k in context.knowledge))
        )

        version = self._repository.next_version(
            context.repository,
            context.branch,
        )

        return TemporalSnapshot(
            snapshot_id=SnapshotRepository.generate_id(),
            version=version,
            repository=context.repository,
            branch=context.branch,
            timestamp=datetime.now().isoformat(),
            version_info=SnapshotVersionInfo(),
            observation_count=len(context.observations),
            measurement_count=len(context.measurements),
            evidence_count=len(package.evidence) if package else 0,
            expertise_count=len(context.expertise_models),
            knowledge_count=len(context.knowledge),
            graph_node_count=graph_node_count,
            graph_edge_count=graph_edge_count,
            expertise_subjects=expertise_subjects,
            knowledge_topics=knowledge_topics,
            org_health=org.health.average_health if org else None,
        )

    # ------------------------------------------------------------------
    # Delta computation
    # ------------------------------------------------------------------

    def compute_delta(
        self,
        current: TemporalSnapshot,
        previous: TemporalSnapshot,
    ) -> TemporalDelta:
        """Compute the difference between two snapshots."""
        try:
            current_dt = datetime.fromisoformat(current.timestamp)
            previous_dt = datetime.fromisoformat(previous.timestamp)
            elapsed = (current_dt - previous_dt).total_seconds()
        except (ValueError, TypeError):
            elapsed = 0.0

        current_subjects = set(current.expertise_subjects)
        previous_subjects = set(previous.expertise_subjects)
        current_topics = set(current.knowledge_topics)
        previous_topics = set(previous.knowledge_topics)

        health_delta = None
        if current.org_health is not None and previous.org_health is not None:
            health_delta = current.org_health - previous.org_health

        return TemporalDelta(
            current_version=current.version,
            previous_version=previous.version,
            time_elapsed_seconds=elapsed,
            observation_delta=current.observation_count - previous.observation_count,
            measurement_delta=current.measurement_count - previous.measurement_count,
            evidence_delta=current.evidence_count - previous.evidence_count,
            expertise_delta=current.expertise_count - previous.expertise_count,
            knowledge_delta=current.knowledge_count - previous.knowledge_count,
            graph_node_delta=current.graph_node_count - previous.graph_node_count,
            graph_edge_delta=current.graph_edge_count - previous.graph_edge_count,
            new_expertise_subjects=tuple(sorted(current_subjects - previous_subjects)),
            lost_expertise_subjects=tuple(sorted(previous_subjects - current_subjects)),
            new_knowledge_topics=tuple(sorted(current_topics - previous_topics)),
            lost_knowledge_topics=tuple(sorted(previous_topics - current_topics)),
            health_delta=health_delta,
        )

    # ------------------------------------------------------------------
    # Trend analysis (velocity, acceleration, momentum)
    # ------------------------------------------------------------------

    def compute_trends(
        self,
        snapshots: tuple[TemporalSnapshot, ...],
        window: int = 5,
    ) -> tuple[TemporalTrend, ...]:
        """Compute trends with velocity, acceleration, and momentum.

        Each numeric metric is analyzed over a rolling window of recent
        snapshots:

        - **Velocity**: change per snapshot (first derivative)
        - **Acceleration**: change in velocity (second derivative)
        - **Momentum**: velocity * window_size (mass analogue)
        - **Direction**: IMPROVING / STABLE / DECLINING

        Uses the most recent ``window`` snapshots (or all if fewer).
        """
        if len(snapshots) < 2:
            return ()

        recent = snapshots[-window:] if len(snapshots) >= window else snapshots

        metrics = {
            "observations": [s.observation_count for s in recent],
            "measurements": [s.measurement_count for s in recent],
            "evidence": [s.evidence_count for s in recent],
            "expertise": [s.expertise_count for s in recent],
            "knowledge": [s.knowledge_count for s in recent],
            "graph_nodes": [s.graph_node_count for s in recent],
            "graph_edges": [s.graph_edge_count for s in recent],
        }

        trends: list[TemporalTrend] = []
        for name, values in metrics.items():
            trend = self._analyze_metric(name, values, len(recent))
            trends.append(trend)

        return tuple(trends)

    def _analyze_metric(
        self,
        name: str,
        values: list[int | float],
        window_size: int,
    ) -> TemporalTrend:
        """Analyze a single metric series."""
        # Velocity: change from second-to-last to last
        velocity = float(values[-1] - values[-2]) if len(values) >= 2 else 0.0

        # Acceleration: change in velocity
        if len(values) >= 3:
            prev_velocity = float(values[-2] - values[-3])
            acceleration = velocity - prev_velocity
        else:
            acceleration = 0.0

        # Momentum: velocity * window_size (mass analogue)
        momentum = velocity * window_size

        # Direction classification
        if velocity > _STABLE_THRESHOLD:
            direction = "IMPROVING"
        elif velocity < -_STABLE_THRESHOLD:
            direction = "DECLINING"
        else:
            direction = "STABLE"

        return TemporalTrend(
            metric_name=name,
            direction=direction,
            velocity=velocity,
            acceleration=acceleration,
            momentum=momentum,
            window_size=window_size,
            values=tuple(float(v) for v in values),
        )

    # ------------------------------------------------------------------
    # Evolution summaries (derived from snapshots, not stored)
    # ------------------------------------------------------------------

    def _expertise_evolution(
        self,
        current: TemporalSnapshot,
        previous: TemporalSnapshot | None,
    ) -> tuple[str, ...]:
        """Describe how expertise has evolved."""
        if previous is None:
            return (
                f"First execution: {current.expertise_count} expertise models "
                f"across {len(current.expertise_subjects)} subjects",
            )

        current_set = set(current.expertise_subjects)
        previous_set = set(previous.expertise_subjects)
        added = sorted(current_set - previous_set)
        removed = sorted(previous_set - current_set)

        descriptions: list[str] = []
        if added:
            descriptions.append(f"New expertise subjects: {', '.join(added[:5])}")
        if removed:
            descriptions.append(f"Lost expertise subjects: {', '.join(removed[:5])}")
        if not added and not removed:
            descriptions.append("Expertise subjects unchanged")
        descriptions.append(
            f"Expertise count: {previous.expertise_count} -> {current.expertise_count}"
        )
        return tuple(descriptions)

    def _knowledge_evolution(
        self,
        current: TemporalSnapshot,
        previous: TemporalSnapshot | None,
    ) -> tuple[str, ...]:
        """Describe how knowledge has evolved."""
        if previous is None:
            return (
                f"First execution: {current.knowledge_count} knowledge models "
                f"across {len(current.knowledge_topics)} topics",
            )

        current_set = set(current.knowledge_topics)
        previous_set = set(previous.knowledge_topics)
        added = sorted(current_set - previous_set)
        removed = sorted(previous_set - current_set)

        descriptions: list[str] = []
        if added:
            descriptions.append(f"New knowledge topics: {', '.join(added[:5])}")
        if removed:
            descriptions.append(f"Lost knowledge topics: {', '.join(removed[:5])}")
        if not added and not removed:
            descriptions.append("Knowledge topics unchanged")
        descriptions.append(
            f"Knowledge count: {previous.knowledge_count} -> {current.knowledge_count}"
        )
        return tuple(descriptions)

    # ------------------------------------------------------------------
    # Historical Context — full lifecycle
    # ------------------------------------------------------------------

    def build_historical_context(
        self,
        context,
    ) -> HistoricalContext:
        """Load history, compute deltas and trends, build context.

        This is the main entry point called by TemporalIntelligenceStage.
        """
        repository = context.repository
        branch = context.branch

        all_snapshots = self._repository.load_all(repository, branch)
        previous = all_snapshots[-1] if all_snapshots else None

        # Build a temporary snapshot for the current execution to use
        # for comparison (this won't be persisted — persistence happens
        # after all stages complete).
        current_temp = self.create_snapshot(context)

        # Delta
        delta = self.compute_delta(current_temp, previous) if previous else None

        # Trends (append the temporary current snapshot for trend computation)
        trend_sequence = (*all_snapshots, current_temp)
        trends = self.compute_trends(trend_sequence)

        # Graph diff
        graph = context.knowledge_graph
        current_nodes = len(getattr(graph, "nodes", [])) if graph else 0
        current_edges = len(getattr(graph, "edges", [])) if graph else 0
        graph_diff = self._graph_diff.diff(current_nodes, current_edges, previous)

        # Evolution summaries (derived, not stored)
        expertise_evo = self._expertise_evolution(current_temp, previous)
        knowledge_evo = self._knowledge_evolution(current_temp, previous)

        return HistoricalContext(
            snapshot_count=len(all_snapshots),
            current_version=current_temp.version,
            previous_snapshot=previous,
            delta=delta,
            trends=trends,
            graph_diff=graph_diff,
            expertise_evolution=expertise_evo,
            knowledge_evolution=knowledge_evo,
            has_history=len(all_snapshots) > 0,
        )
