from typing import Any, Dict, List, Set
from app.kernel.graph import GraphEngine, GraphNode, NodeType, EdgeType

class PatternMatcher:
    """
    Detects static structural patterns (Anti-patterns & Healthy patterns) 
    in the Reasoning Graph deterministically.
    """
    def __init__(self, graph: GraphEngine):
        self.graph = graph

    def match_single_point_of_failure(self) -> List[GraphNode]:
        """
        Pattern: [EVIDENCE: bus_factor <= 1] <--- [EVIDENCE: ownership == High]
        This looks for structurally related evidence without relying on the RuleEngine's logic.
        """
        matches = []
        evidence_nodes = self.graph.get_all_nodes(NodeType.EVIDENCE)
        
        for node in evidence_nodes:
            raw = node.properties.get("raw_output", {})
            if raw.get("bus_factor", 99) <= 1:
                # We found a bus factor 1 node. Are there correlated high ownership nodes?
                # A correlation edge might exist, or they might support the same inference.
                # Let's search neighbors.
                neighbors = self.graph.get_neighbors(node.id, direction="both")
                for n in neighbors:
                    if n.node_type == NodeType.EVIDENCE and n.properties.get("raw_output", {}).get("ownership") == "High":
                        matches.append(node)
                        break
                        
        return matches

    def run_all_patterns(self) -> Dict[str, List[GraphNode]]:
        """Executes all registered static patterns and returns matched anchor nodes."""
        return {
            "Single Point of Failure": self.match_single_point_of_failure()
        }
