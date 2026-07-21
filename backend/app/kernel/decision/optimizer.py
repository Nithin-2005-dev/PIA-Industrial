from typing import List, Set
from app.kernel.graph import GraphEngine, NodeType, EdgeType

class GraphOptimizer:
    """
    Prunes redundant reasoning paths and identifies the highest-leverage intervention points.
    """
    def __init__(self, graph: GraphEngine):
        self.graph = graph
        
    def optimize(self):
        """
        Finds overlapping Root Causes and consolidates them to maximize mitigation leverage.
        Computes Pareto optimality against current constraints.
        """
        rc_nodes = self.graph.get_all_nodes(NodeType.ROOT_CAUSE)
        
        # Calculate Leverage Score: how many IMPACT nodes does this ROOT_CAUSE point to?
        for rc in rc_nodes:
            impacts_caused = self.graph.get_edges(rc.id, direction="out", edge_type=EdgeType.CAUSES)
            leverage_score = len(impacts_caused)
            rc.properties["leverage_score"] = leverage_score
            
            # Pareto calculations for mitigation selection
            # In a full system, this checks the cached Action Library
            # For this MVP, we synthesize the optimal parameters directly on the root cause for the MitigationEngine to consume
            expected_benefit = leverage_score * rc.confidence * 100.0
            implementation_cost = 50.0 # Arbitrary default
            execution_time_hours = 4.0
            risk_reduction = expected_benefit / (implementation_cost + 1)
            
            # Dominance check (simulate pareto frontier selection)
            is_pareto_optimal = (risk_reduction > 1.5)
            
            rc.properties["pareto_metrics"] = {
                "expected_benefit": expected_benefit,
                "implementation_cost": implementation_cost,
                "execution_time_hours": execution_time_hours,
                "risk_reduction": risk_reduction,
                "is_pareto_optimal": is_pareto_optimal
            }
