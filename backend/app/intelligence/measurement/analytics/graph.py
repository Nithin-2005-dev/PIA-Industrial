from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class GraphMeasurementResult:
    node_count: int
    edge_count: int
    density: float
    degree_centrality: dict[str, float]
    strongly_connected_components: list[tuple[str, ...]]


class GraphMeasurementEngine:

    def measure(
        self,
        edges: list[tuple[str, str]],
    ) -> GraphMeasurementResult:
        nodes = set()
        outgoing = defaultdict(set)
        incoming = defaultdict(set)

        for source, target in edges:
            nodes.add(
                source
            )
            nodes.add(
                target
            )
            outgoing[source].add(
                target
            )
            incoming[target].add(
                source
            )

        node_count = len(
            nodes
        )

        edge_count = len(
            edges
        )

        possible_edges = node_count * (
            node_count - 1
        )

        density = (
            edge_count / possible_edges
            if possible_edges > 0
            else 0.0
        )

        degree_centrality = {}

        for node in nodes:
            degree = len(
                outgoing[node]
            ) + len(
                incoming[node]
            )
            degree_centrality[node] = (
                degree / max(
                    1,
                    node_count - 1,
                )
            )

        return GraphMeasurementResult(
            node_count=node_count,
            edge_count=edge_count,
            density=density,
            degree_centrality=degree_centrality,
            strongly_connected_components=(
                self._strongly_connected_components(
                    nodes,
                    outgoing,
                )
            ),
        )

    def _strongly_connected_components(
        self,
        nodes,
        outgoing,
    ) -> list[tuple[str, ...]]:
        index = 0
        stack = []
        indices = {}
        lowlinks = {}
        on_stack = set()
        components = []

        def visit(node):
            nonlocal index

            indices[node] = index
            lowlinks[node] = index
            index += 1
            stack.append(
                node
            )
            on_stack.add(
                node
            )

            for target in outgoing[node]:
                if target not in indices:
                    visit(
                        target
                    )
                    lowlinks[node] = min(
                        lowlinks[node],
                        lowlinks[target],
                    )
                elif target in on_stack:
                    lowlinks[node] = min(
                        lowlinks[node],
                        indices[target],
                    )

            if lowlinks[node] == indices[node]:
                component = []

                while True:
                    target = stack.pop()
                    on_stack.remove(
                        target
                    )
                    component.append(
                        target
                    )

                    if target == node:
                        break

                components.append(
                    tuple(
                        sorted(
                            component
                        )
                    )
                )

        for node in nodes:
            if node not in indices:
                visit(
                    node
                )

        return sorted(
            components,
            key=lambda component: (
                -len(component),
                component,
            ),
        )


