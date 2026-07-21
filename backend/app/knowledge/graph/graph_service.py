from app.knowledge.graph.organizational_graph import (
    OrganizationalGraph,
)


class GraphService:

    def __init__(
        self,
        graph: OrganizationalGraph,
    ):
        self._graph = graph

    def outgoing(
        self,
        node_id: str,
    ):

        return [
            edge
            for edge in self._graph.edges
            if edge.source_id == node_id
        ]

    def incoming(
        self,
        node_id: str,
    ):

        return [
            edge
            for edge in self._graph.edges
            if edge.target_id == node_id
        ]

    def neighbors(
        self,
        node_id: str,
    ):

        neighbor_ids = set()

        for edge in self._graph.edges:

            if edge.source_id == node_id:

                neighbor_ids.add(
                    edge.target_id
                )

            elif edge.target_id == node_id:

                neighbor_ids.add(
                    edge.source_id
                )

        return [
            node
            for node in self._graph.nodes
            if node.id in neighbor_ids
        ]

    def find_by_relationship(
        self,
        relationship: str,
    ):

        return [
            edge
            for edge in self._graph.edges
            if (
                edge.relationship
                == relationship
            )
        ]

    def nodes_by_type(
        self,
        node_type: str,
    ):
        normalized = node_type.upper()
        return [
            node
            for node in self._graph.nodes
            if node.type.upper() == normalized
        ]

    def degree_centrality(
        self,
    ) -> dict[str, float]:
        if len(self._graph.nodes) <= 1:
            return {
                node.id: 0.0
                for node in self._graph.nodes
            }
        degrees = {
            node.id: 0
            for node in self._graph.nodes
        }
        for edge in self._graph.edges:
            degrees[edge.source_id] = degrees.get(edge.source_id, 0) + 1
            degrees[edge.target_id] = degrees.get(edge.target_id, 0) + 1
        scale = len(self._graph.nodes) - 1
        return {
            node_id: degree / scale
            for node_id, degree in degrees.items()
        }

    def shortest_path(
        self,
        source_id: str,
        target_id: str,
    ) -> list[str]:
        if source_id == target_id:
            return [source_id]

        adjacency: dict[str, set[str]] = {}
        for edge in self._graph.edges:
            adjacency.setdefault(edge.source_id, set()).add(edge.target_id)
            adjacency.setdefault(edge.target_id, set()).add(edge.source_id)

        visited = {source_id}
        queue: list[list[str]] = [[source_id]]
        while queue:
            path = queue.pop(0)
            node_id = path[-1]
            for neighbor_id in sorted(adjacency.get(node_id, ())):
                if neighbor_id in visited:
                    continue
                next_path = [*path, neighbor_id]
                if neighbor_id == target_id:
                    return next_path
                visited.add(neighbor_id)
                queue.append(next_path)
        return []

    def subgraph(
        self,
        node_ids: set[str],
    ):
        from app.knowledge.graph.organizational_graph import OrganizationalGraph

        return OrganizationalGraph(
            nodes=[
                node
                for node in self._graph.nodes
                if node.id in node_ids
            ],
            edges=[
                edge
                for edge in self._graph.edges
                if (
                    edge.source_id in node_ids
                    and edge.target_id in node_ids
                )
            ],
        )
