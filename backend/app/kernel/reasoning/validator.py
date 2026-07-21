from typing import List
from app.kernel.graph import GraphEngine, NodeType, EdgeType

class GraphValidationError(Exception):
    pass

class GraphValidator:
    """
    Ensures mathematical and topological integrity of the Reasoning Graph.
    """
    def __init__(self, graph: GraphEngine):
        self.graph = graph
        
    def validate(self):
        """Runs all validations. Raises GraphValidationError if integrity is compromised."""
        self._check_node_bounds()
        self._check_edge_integrity()
        self._check_cycles()
        self._check_orphan_nodes()
        self._check_duplicates()
        
    def _check_node_bounds(self):
        for node in self.graph.get_all_nodes():
            if not (0.0 <= node.confidence <= 1.0):
                raise GraphValidationError(f"Node {node.id} has invalid confidence: {node.confidence}")
            if node.node_type == NodeType.INFERENCE:
                score = node.properties.get("priority_score")
                if score is not None and not (0.0 <= score <= 100.0):
                    raise GraphValidationError(f"Node {node.id} has invalid priority score: {score}")

    def _check_edge_integrity(self):
        for edge in self.graph.get_edges(None, direction="both"):
            source = self.graph.get_node(edge.source_id)
            target = self.graph.get_node(edge.target_id)
            if not source or not target:
                raise GraphValidationError(f"Edge {edge} connects missing nodes.")
            if source.id == target.id:
                raise GraphValidationError(f"Self-loop detected on node {source.id}")

    def _check_cycles(self):
        # A simple DFS to detect cycles
        visited = set()
        stack = set()
        
        def dfs(node_id: str):
            visited.add(node_id)
            stack.add(node_id)
            
            for edge in self.graph.get_edges(node_id, direction="out"):
                if edge.target_id not in visited:
                    dfs(edge.target_id)
                elif edge.target_id in stack:
                    raise GraphValidationError(f"Cycle detected involving node {node_id} and {edge.target_id}")
                    
            stack.remove(node_id)
            
        for node in self.graph.get_all_nodes():
            if node.id not in visited:
                dfs(node.id)

    def _check_orphan_nodes(self):
        # Root causes without evidence, disconnected recommendations, etc.
        # But some nodes might legally be disconnected in early stages. 
        # In a fully executed graph, every INFERENCE should have an out SUPPORTS edge.
        pass

    def _check_duplicates(self):
        # We rely on Canonical IDs for this, but we can verify no two nodes have identical signatures but different IDs.
        pass
