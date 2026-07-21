"""Graph Diff Engine — computes structural differences between knowledge graphs.

M52 implements metric-level diffing (node/edge count comparison).
Full structural node-level diffing with identity tracking is deferred
to M54 (Graph Analytics) where it belongs architecturally.
"""

from __future__ import annotations

from app.intelligence.temporal.models import GraphDiffResult
from app.intelligence.temporal.models import TemporalSnapshot


class GraphDiffEngine:
    """Computes the structural difference between two knowledge graph states.

    The current graph state is taken from the live PlatformContext.
    The previous graph state is reconstructed from a TemporalSnapshot.
    """

    def diff(
        self,
        current_node_count: int,
        current_edge_count: int,
        previous_snapshot: TemporalSnapshot | None,
    ) -> GraphDiffResult:
        """Compare current graph metrics against the previous snapshot.

        If there is no previous snapshot, returns a diff showing
        everything as newly added.
        """
        if previous_snapshot is None:
            return GraphDiffResult(
                nodes_added=current_node_count,
                nodes_removed=0,
                edges_added=current_edge_count,
                edges_removed=0,
                summary=(
                    f"First execution: {current_node_count} nodes, "
                    f"{current_edge_count} edges (no prior graph)"
                ),
            )

        prev_nodes = previous_snapshot.graph_node_count
        prev_edges = previous_snapshot.graph_edge_count

        node_delta = current_node_count - prev_nodes
        edge_delta = current_edge_count - prev_edges

        # Approximate additions/removals from the net delta.
        # Full structural tracking (M54) will provide exact counts.
        nodes_added = max(0, node_delta)
        nodes_removed = max(0, -node_delta)
        edges_added = max(0, edge_delta)
        edges_removed = max(0, -edge_delta)

        parts: list[str] = []
        if node_delta > 0:
            parts.append(f"+{node_delta} nodes")
        elif node_delta < 0:
            parts.append(f"{node_delta} nodes")
        else:
            parts.append("nodes unchanged")

        if edge_delta > 0:
            parts.append(f"+{edge_delta} edges")
        elif edge_delta < 0:
            parts.append(f"{edge_delta} edges")
        else:
            parts.append("edges unchanged")

        summary = f"Graph diff: {', '.join(parts)}"

        return GraphDiffResult(
            nodes_added=nodes_added,
            nodes_removed=nodes_removed,
            edges_added=edges_added,
            edges_removed=edges_removed,
            summary=summary,
        )
