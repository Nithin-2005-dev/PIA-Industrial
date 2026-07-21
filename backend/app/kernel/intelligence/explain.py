from typing import Any, Dict, List
from app.kernel.graph import GraphEngine, GraphNode

class ExplainabilityAPI:
    """
    Traverses backward from any GraphNode to yield its exact supporting evidence,
    fired rules, and confidence lineage.
    """
    def __init__(self, graph: GraphEngine):
        self.graph = graph

    def explain(self, node_id: str) -> Dict[str, Any]:
        target_node = self.graph.get_node(node_id)
        if not target_node:
            return {"error": "Node not found"}
            
        explanation = {
            "node_id": target_node.id,
            "node_type": target_node.node_type.value,
            "properties": target_node.properties,
            "confidence": target_node.confidence,
            "lineage": []
        }
        
        # Traverse backward to find supporting evidence
        # (This is simplified for Phase 3 - just doing a 5-hop DFS)
        # In the graph, CAUSES edges point from IMPACT -> INFERENCE
        # SUPPORTS edges point from INFERENCE -> OBSERVATION
        # DERIVED_FROM edges point from OBSERVATION -> EVIDENCE
        paths = []
        evidence_nodes = self.graph.get_all_nodes(node_type=None)
        
        # Find paths from this node back to all leaves (EVIDENCE nodes)
        # Actually our graph edges are directed towards the source (target_id is the source of the fact)
        # Wait, in builder: `target_id=inf.id, source_id=impact.id`. So impact -> inference.
        for ev in evidence_nodes:
            if ev.node_type.value == "evidence":
                found_paths = self.graph.find_paths(node_id, ev.id, max_depth=5)
                if found_paths:
                    for p in found_paths:
                        paths.append([n.node_type.value for n in p])
                        
        explanation["lineage"] = paths
        return explanation
