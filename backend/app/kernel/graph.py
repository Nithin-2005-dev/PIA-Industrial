from typing import Any, Dict, List, Optional
import dataclasses
from enum import Enum

class NodeType(Enum):
    EVIDENCE = "evidence"
    OBSERVATION = "observation"
    INFERENCE = "inference"
    CONFLICT = "conflict"
    ROOT_CAUSE = "root_cause"
    RECOMMENDATION = "recommendation"
    IMPACT = "impact"

class EdgeType(Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    CAUSES = "causes"
    DEPENDS_ON = "depends_on"
    MITIGATES = "mitigates"
    EXTENDS = "extends"
    CORRELATES = "correlates"
    CONTAINS = "contains"
    DERIVED_FROM = "derived_from"
    VERIFIED_BY = "verified_by"

@dataclasses.dataclass(frozen=True)
class GraphNode:
    id: str
    node_type: NodeType
    properties: Dict[str, Any]
    confidence: float = 1.0
    
    @staticmethod
    def generate_id(node_type: NodeType, semantic_target: str = "", rule_id: str = "", cluster_id: str = "", ontology_path: str = "") -> str:
        """Generates a deterministic canonical ID based on architectural taxonomy."""
        import hashlib
        core_string = f"{node_type.value}|{semantic_target}|{rule_id}|{cluster_id}|{ontology_path}"
        return f"{node_type.value}_{hashlib.sha256(core_string.encode('utf-8')).hexdigest()[:12]}"

@dataclasses.dataclass(frozen=True)
class GraphEdge:
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0

class GraphEngine:
    """
    Manages the fully typed, deterministic Reasoning Graph.
    """
    def __init__(self):
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: List[GraphEdge] = []
        
    def add_node(self, node: GraphNode) -> GraphNode:
        """Merges node. Returns existing node if ID already present to maintain true DAG."""
        if node.id in self._nodes:
            # Optionally merge properties here, but for now we retain the first instantiated canonical node.
            return self._nodes[node.id]
        self._nodes[node.id] = node
        return node
        
    def add_edge(self, edge: GraphEdge) -> GraphEdge:
        """Merges edge. Prevents duplicate multigraph edges."""
        if edge.source_id not in self._nodes or edge.target_id not in self._nodes:
            raise ValueError(f"Cannot add edge: Nodes {edge.source_id} or {edge.target_id} do not exist.")
            
        for e in self._edges:
            if e.source_id == edge.source_id and e.target_id == edge.target_id and e.edge_type == edge.edge_type:
                return e # Duplicate edge prevented
                
        self._edges.append(edge)
        return edge
        
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self._nodes.get(node_id)
        
    def get_all_nodes(self, node_type: Optional[NodeType] = None) -> List[GraphNode]:
        if node_type:
            return [n for n in self._nodes.values() if n.node_type == node_type]
        return list(self._nodes.values())

    def get_edges(self, node_id: str, direction: str = "both", edge_type: Optional[EdgeType] = None) -> List[GraphEdge]:
        edges = []
        for e in self._edges:
            if edge_type and e.edge_type != edge_type:
                continue
            if direction in ("out", "both") and e.source_id == node_id:
                edges.append(e)
            elif direction in ("in", "both") and e.target_id == node_id:
                edges.append(e)
        return edges

    def get_neighbors(self, node_id: str, direction: str = "out", edge_type: Optional[EdgeType] = None) -> List[GraphNode]:
        neighbors = []
        edges = self.get_edges(node_id, direction, edge_type)
        for e in edges:
            if e.source_id == node_id:
                n = self.get_node(e.target_id)
            else:
                n = self.get_node(e.source_id)
            if n:
                neighbors.append(n)
        return neighbors

    def find_paths(self, start_id: str, end_id: str, max_depth: int = 5) -> List[List[GraphNode]]:
        """DFS to find all paths between start and end nodes up to max_depth."""
        paths = []
        start_node = self.get_node(start_id)
        end_node = self.get_node(end_id)
        if not start_node or not end_node:
            return paths

        def dfs(current_id: str, current_path: List[GraphNode], depth: int):
            if depth > max_depth:
                return
            if current_id == end_id:
                paths.append(list(current_path))
                return
                
            neighbors = self.get_neighbors(current_id, direction="out")
            for neighbor in neighbors:
                if neighbor not in current_path: # avoid cycles
                    current_path.append(neighbor)
                    dfs(neighbor.id, current_path, depth + 1)
                    current_path.pop()

        dfs(start_id, [start_node], 0)
        return paths

    def get_downstream_subgraph(self, node_ids: List[str]) -> List[GraphNode]:
        """Finds all nodes affected by the given starting nodes (incremental updates)."""
        affected = set()
        queue = list(node_ids)
        
        while queue:
            current = queue.pop(0)
            if current not in affected:
                affected.add(current)
                # Find nodes where current is the source_id (downstream impact)
                neighbors = self.get_neighbors(current, direction="out")
                for n in neighbors:
                    if n.id not in affected:
                        queue.append(n.id)
                        
        return [self.get_node(nid) for nid in affected if self.get_node(nid)]

    def explain(self, node_id: str) -> List[Dict[str, Any]]:
        """Walks backwards to generate a human-readable lineage trace for explainability."""
        node = self.get_node(node_id)
        if not node:
            return []
            
        trace = []
        visited = set()
        
        def walk_backward(current_id: str, depth: int):
            if current_id in visited or depth > 10:
                return
            visited.add(current_id)
            
            curr_node = self.get_node(current_id)
            if not curr_node:
                return
                
            trace.append({
                "depth": depth,
                "node_type": curr_node.node_type.value,
                "id": curr_node.id,
                "properties": curr_node.properties
            })
            
            # Walk backward along specific edges
            incoming_edges = self.get_edges(current_id, direction="in")
            for e in incoming_edges:
                walk_backward(e.source_id, depth + 1)
                
        walk_backward(node_id, 0)
        # Sort trace by depth descending to show Evidence -> Observation -> Inference
        trace.sort(key=lambda x: x["depth"], reverse=True)
        return trace
