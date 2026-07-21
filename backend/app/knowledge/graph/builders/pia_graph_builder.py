from app.knowledge.graph.graph_edge import (
    GraphEdge,
)

from app.knowledge.graph.graph_node import (
    GraphNode,
)

from app.knowledge.graph.organizational_graph import (
    OrganizationalGraph,
)


class PIAGraphBuilder:

    def build(
        self,
        ownership_estimates,
        knowledge_risks,
        successor_candidates,
    ) -> OrganizationalGraph:

        nodes = {}
        edges = []

        #
        # Ownership
        #

        for ownership in ownership_estimates:

            developer_id = (
                ownership.owner_ref.id
            )

            module_id = (
                ownership.module_ref.id
            )

            nodes[developer_id] = GraphNode(
                id=developer_id,
                type="DEVELOPER",
            )

            nodes[module_id] = GraphNode(
                id=module_id,
                type="MODULE",
            )

            edges.append(
                GraphEdge(
                    source_id=developer_id,
                    target_id=module_id,
                    relationship="OWNS",
                    weight=(
                        ownership
                        .ownership_percentage
                    ),
                )
            )

        #
        # Risk
        #

        for risk in knowledge_risks:

            module_id = (
                risk.module_ref.id
            )

            risk_node_id = (
                f"risk:{module_id}"
            )

            nodes[risk_node_id] = (
                GraphNode(
                    id=risk_node_id,
                    type="RISK",
                )
            )

            edges.append(
                GraphEdge(
                    source_id=module_id,
                    target_id=risk_node_id,
                    relationship="RISK",
                    weight=float(
                        risk.bus_factor
                    ),
                )
            )

        #
        # Successor
        #

        for candidate in (
            successor_candidates
        ):

            developer_id = (
                candidate.developer_ref.id
            )

            module_id = (
                candidate.module_ref.id
            )

            nodes[developer_id] = (
                GraphNode(
                    id=developer_id,
                    type="DEVELOPER",
                )
            )

            edges.append(
                GraphEdge(
                    source_id=developer_id,
                    target_id=module_id,
                    relationship="SUCCESSOR",
                    weight=candidate.score,
                )
            )

        return OrganizationalGraph(
            nodes=list(nodes.values()),
            edges=edges,
        )