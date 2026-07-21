import uuid
from typing import List, Dict, Any
from app.kernel.graph import GraphEngine, GraphNode, NodeType, GraphEdge, EdgeType

class RootCauseAnalyzer:
    """
    Traverses the Reasoning Graph backward from IMPACT nodes to isolate ROOT_CAUSE nodes.
    """
    def __init__(self, graph: GraphEngine):
        self.graph = graph
        
    def analyze_root_causes(self):
        impacts = self.graph.get_all_nodes(NodeType.IMPACT)
        for impact in impacts:
            self._trace_impact_to_root(impact)
            
    def _trace_impact_to_root(self, impact: GraphNode):
        """
        Walks backwards: IMPACT -> CAUSES -> INFERENCE -> SUPPORTS -> OBSERVATION -> DERIVED_FROM -> EVIDENCE
        Finds the fundamental evidence and flags it as a Root Cause.
        """
        # simplified DFS to find all EVIDENCE leaf nodes reachable by following incoming edges backward.
        # But wait, edge directions: 
        # INFERENCE -(SUPPORTS)-> OBSERVATION
        # IMPACT -(CAUSES)-> INFERENCE
        
        leaf_evidence_nodes = []
        visited = set()
        
        def dfs(current_id: str):
            if current_id in visited:
                return
            visited.add(current_id)
            
            node = self.graph.get_node(current_id)
            if not node:
                return
                
            if node.node_type == NodeType.EVIDENCE:
                leaf_evidence_nodes.append(node)
                return
                
            # Follow edges where the current node is the SOURCE
            # IMPACT -(CAUSES)-> INFERENCE. Source=Impact, Target=Inference.
            neighbors = self.graph.get_neighbors(current_id, direction="out")
            for neighbor in neighbors:
                dfs(neighbor.id)
                
        dfs(impact.id)
        
        # Consolidate leaf evidence into ROOT CAUSE nodes
        for ev in leaf_evidence_nodes:
            rc_id = GraphNode.generate_id(NodeType.ROOT_CAUSE, semantic_target=ev.properties.get("entity", "Unknown"))
            
            # Extract possible rule metadata from downstream inferences
            rule_id = "unknown"
            rule_version = "unknown"
            # Find downstream inference to extract rule info
            inferences = [n for n in self.graph.get_downstream_subgraph([ev.id]) if n.node_type == NodeType.INFERENCE]
            if inferences:
                # We can't strictly know which rule without backwards property passing, but for MVP:
                rule_id = inferences[0].id # Just to show it's tracked
            
            rc_node = GraphNode(
                id=rc_id,
                node_type=NodeType.ROOT_CAUSE,
                properties={
                    "title": f"Root Cause: {ev.properties.get('domain', 'Anomaly')}",
                    "description": f"Fundamental root cause identified in {ev.properties.get('entity', 'Unknown')}. Supports {len(inferences)} downstream inferences.",
                    "severity": impact.confidence, # Propagate confidence
                    "generated_by": "RootCauseAnalyzer_v1",
                    "rule_id": rule_id,
                    "rule_version": rule_version,
                    "dependencies": [ev.id]
                },
                confidence=ev.confidence
            )
            rc_node = self.graph.add_node(rc_node)
            
            # Connect ROOT_CAUSE to the IMPACT it causes
            edge = GraphEdge(
                source_id=rc_node.id,
                target_id=impact.id,
                edge_type=EdgeType.CAUSES,
                weight=1.0
            )
            self.graph.add_edge(edge)
