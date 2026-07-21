import uuid
from typing import List
from app.kernel.graph import GraphEngine, GraphNode, NodeType, GraphEdge, EdgeType

class MitigationEngine:
    """
    Deterministically maps ROOT_CAUSE nodes to actionable RECOMMENDATION nodes.
    """
    def __init__(self, graph: GraphEngine):
        self.graph = graph
        
    def generate_mitigations(self):
        rc_nodes = self.graph.get_all_nodes(NodeType.ROOT_CAUSE)
        
        for rc in rc_nodes:
            # Deterministic lookup table logic for mitigations
            desc = rc.properties.get("description", "").lower()
            
            action = "Review system architecture."
            if "bus factor" in desc:
                action = "Trigger cross-training protocol for critical module."
            elif "ownership" in desc:
                action = "Distribute ownership to secondary team members."
                
            pareto_metrics = rc.properties.get("pareto_metrics", {})
            if not pareto_metrics.get("is_pareto_optimal", True):
                # Skip suboptimal recommendations
                continue
                
            rec_id = GraphNode.generate_id(NodeType.RECOMMENDATION, semantic_target=rc.properties.get("entity", "System"), rule_id=rc.properties.get("rule_id", ""))
            
            rec_node = GraphNode(
                id=rec_id,
                node_type=NodeType.RECOMMENDATION,
                properties={
                    "action": action,
                    "leverage_score": rc.properties.get("leverage_score", 1),
                    "status": "PENDING_ALLOCATION",
                    "expected_benefit": pareto_metrics.get("expected_benefit"),
                    "implementation_cost": pareto_metrics.get("implementation_cost"),
                    "execution_time_hours": pareto_metrics.get("execution_time_hours"),
                    "risk_reduction": pareto_metrics.get("risk_reduction"),
                    "confidence": rc.confidence
                },
                confidence=rc.confidence
            )
            rec_node = self.graph.add_node(rec_node)
            
            # Connect Recommendation -> Mitigates -> Root Cause
            edge = GraphEdge(
                source_id=rec_node.id,
                target_id=rc.id,
                edge_type=EdgeType.MITIGATES,
                weight=1.0
            )
            self.graph.add_edge(edge)
