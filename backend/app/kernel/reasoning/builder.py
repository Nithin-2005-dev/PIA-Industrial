from typing import Any, List
import uuid

from app.kernel.graph import GraphEngine, GraphNode, NodeType, GraphEdge, EdgeType
from app.kernel.reasoning.fusion import EvidenceFusion
from app.kernel.models import CapabilityResult

class ReasoningGraphBuilder:
    """
    Constructs the Reasoning Graph by taking fused evidence and applying Observations.
    """
    def __init__(self, graph: GraphEngine):
        self.graph = graph
        
    def build_from_results(self, results: List[CapabilityResult]):
        fusion = EvidenceFusion()
        evidence_nodes = fusion.fuse(results)
        
        # Add Evidence to Graph
        for node in fusion.to_graph_nodes():
            self.graph.add_node(node)
            
            # For each piece of evidence, create an explicit Observation node.
            # Evidence -> (derived_from) -> Observation
            obs_id = GraphNode.generate_id(NodeType.OBSERVATION, semantic_target=node.properties.get("entity", "Unknown"))
            
            obs_node = GraphNode(
                id=obs_id,
                node_type=NodeType.OBSERVATION,
                properties={"description": f"Observed from {node.id}"},
                confidence=node.confidence
            )
            obs_node = self.graph.add_node(obs_node)
            
            edge = GraphEdge(
                source_id=obs_node.id,
                target_id=node.id,
                edge_type=EdgeType.DERIVED_FROM,
                weight=1.0
            )
            self.graph.add_edge(edge)
