"""Temporal Intelligence domain models.

All models are frozen and immutable.  Snapshots are the source of truth;
deltas, trends, and historical context are derived views that can always
be recomputed from the snapshot sequence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Snapshot version metadata — ensures replay reproducibility even after
# algorithm changes across milestones.
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class SnapshotVersionInfo:
    """Records the exact software versions used to produce a snapshot."""
    runtime_version: str = "1.0"
    pipeline_schema_version: str = "1.0"
    measurement_algorithm_version: str = "1.0"
    evidence_algorithm_version: str = "1.0"
    graph_version: str = "1.0"


# ---------------------------------------------------------------------------
# Temporal Snapshot — immutable record of a single pipeline execution
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class TemporalSnapshot:
    """Immutable record of one canonical pipeline execution.

    This is the atomic unit of temporal intelligence.  Every successful
    pipeline run produces exactly one TemporalSnapshot.  The snapshot
    contains enough information to compute deltas, trends, velocity,
    acceleration, and momentum against any other snapshot.
    """
    snapshot_id: str
    version: int
    repository: str
    branch: str
    timestamp: str
    version_info: SnapshotVersionInfo

    # Pipeline layer counts
    observation_count: int
    measurement_count: int
    evidence_count: int
    expertise_count: int
    knowledge_count: int
    graph_node_count: int
    graph_edge_count: int

    # Structural identity sets (for diffing)
    expertise_subjects: tuple[str, ...]
    knowledge_topics: tuple[str, ...]

    # Org intelligence summary (may be None on first run)
    org_health: float | None

    # Extensible metadata bucket
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Temporal Delta — difference between two snapshots
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class TemporalDelta:
    """The difference between the current and previous snapshot.

    All fields are derived from comparing two TemporalSnapshot instances.
    """
    current_version: int
    previous_version: int
    time_elapsed_seconds: float

    observation_delta: int
    measurement_delta: int
    evidence_delta: int
    expertise_delta: int
    knowledge_delta: int
    graph_node_delta: int
    graph_edge_delta: int

    new_expertise_subjects: tuple[str, ...]
    lost_expertise_subjects: tuple[str, ...]
    new_knowledge_topics: tuple[str, ...]
    lost_knowledge_topics: tuple[str, ...]

    health_delta: float | None


# ---------------------------------------------------------------------------
# Temporal Trend — direction, velocity, acceleration, and momentum
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class TemporalTrend:
    """Trend analysis for a single metric across a rolling window.

    The calculus of knowledge:
      State       → the current value
      Delta       → change from previous snapshot
      Velocity    → rate of change (first derivative)
      Acceleration → change in velocity (second derivative)
      Momentum    → velocity × mass (where mass = snapshot count in window)

    Momentum captures both the speed and the inertia of a trend.  A trend
    with high velocity but small window has low momentum (could reverse).
    A trend with moderate velocity but large window has high momentum
    (unlikely to reverse quickly).  This becomes critical for forecasting.
    """
    metric_name: str
    direction: str            # IMPROVING / STABLE / DECLINING
    velocity: float           # first derivative
    acceleration: float       # second derivative
    momentum: float           # velocity * window_size (mass analogue)
    window_size: int
    values: tuple[float, ...]


# ---------------------------------------------------------------------------
# Graph Diff Result — structural difference between knowledge graphs
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class GraphDiffResult:
    """Metric-level diff between two knowledge graph snapshots.

    Full structural node-level diffing is deferred to M54 (Graph Analytics).
    M52 tracks aggregate counts which are sufficient for trend computation.
    """
    nodes_added: int
    nodes_removed: int
    edges_added: int
    edges_removed: int
    summary: str


# ---------------------------------------------------------------------------
# Historical Context — the complete temporal view injected into the pipeline
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class HistoricalContext:
    """Complete temporal context injected into the canonical pipeline.

    This is the output contract of the Temporal Intelligence stage.
    Downstream stages (Organization Intelligence, Reasoning, Decision,
    Executive) consume this to make time-aware conclusions.

    Snapshots are the source of truth.  Every field in this context is
    a derived view that can be recomputed from the snapshot sequence.
    """
    snapshot_count: int
    current_version: int
    previous_snapshot: TemporalSnapshot | None
    delta: TemporalDelta | None
    trends: tuple[TemporalTrend, ...]
    graph_diff: GraphDiffResult | None
    expertise_evolution: tuple[str, ...]
    knowledge_evolution: tuple[str, ...]
    has_history: bool
