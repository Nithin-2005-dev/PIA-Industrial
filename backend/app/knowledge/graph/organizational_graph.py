from dataclasses import dataclass

from .graph_node import GraphNode
from .graph_edge import GraphEdge


@dataclass(frozen=True)
class OrganizationalGraph:
    """
    Organizational knowledge graph.
    """

    nodes: list[GraphNode]

    edges: list[GraphEdge]