from app.graph.graph_node import (
    GraphNode,
)

from app.graph.graph_edge import (
    GraphEdge,
)

from app.graph.organizational_graph import (
    OrganizationalGraph,
)


def main():

    developer = GraphNode(
        id="alice",
        type="DEVELOPER",
    )

    module = GraphNode(
        id="auth.py",
        type="MODULE",
    )

    expertise_edge = GraphEdge(
        source_id="alice",
        target_id="auth.py",
        relationship="EXPERTISE",
        weight=82.0,
    )

    graph = OrganizationalGraph(
        nodes=[
            developer,
            module,
        ],
        edges=[
            expertise_edge,
        ],
    )

    print(
        "\n=== GRAPH DOMAIN ===\n"
    )

    print(
        f"Nodes: {len(graph.nodes)}"
    )

    print(
        f"Edges: {len(graph.edges)}"
    )

    for edge in graph.edges:

        print(
            f"{edge.source_id}"
            f" --{edge.relationship}--> "
            f"{edge.target_id}"
        )


if __name__ == "__main__":
    main()