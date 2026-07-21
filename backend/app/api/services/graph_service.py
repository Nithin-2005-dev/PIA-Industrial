from typing import Optional, List, Set, Tuple
from collections import deque
from app.kernel.graph import GraphEngine, GraphNode, GraphEdge
from app.api.dtos.v1 import GraphNodeDTO_v1, GraphEdgeDTO_v1, GraphResponseDTO_v1

class GraphService:
    def __init__(self, graph_engine: GraphEngine):
        self.graph = graph_engine

    def get_filtered_graph(
        self, 
        node_id: Optional[str] = None, 
        depth: int = 2, 
        limit: int = 100, 
        offset: int = 0,
        node_types: Optional[List[str]] = None,
        view: str = "knowledge"
    ) -> GraphResponseDTO_v1:
        
        all_nodes = self.graph.get_all_nodes()
        all_edges = self.graph._edges
        
        # Filter nodes by view mode
        # knowledge: modules, developers, concepts
        # reasoning: evidence, inference, rules
        # execution: trace, capability, intention
        if view == "knowledge":
            allowed_types = {"module", "developer", "concept", "file"}
        elif view == "reasoning":
            allowed_types = {"evidence", "inference", "rule", "observation"}
        elif view == "execution":
            allowed_types = {"trace", "capability", "intention", "step"}
        else:
            allowed_types = set()

        filtered_nodes = [n for n in all_nodes if (not allowed_types or n.node_type.value in allowed_types)]
        
        if node_types:
            filtered_nodes = [n for n in filtered_nodes if n.node_type.value in node_types]
            
        # If node_id provided, do a BFS up to `depth` hops
        if node_id:
            node_map = {n.id: n for n in all_nodes}
            if node_id not in node_map:
                return GraphResponseDTO_v1(nodes=[], edges=[], total_nodes=0, truncated=False)
                
            visited_nodes: Set[str] = set()
            queue = deque([(node_id, 0)])
            visited_nodes.add(node_id)
            
            # Fast edge lookup
            adj_list = {}
            for e in all_edges:
                if e.source_id not in adj_list: adj_list[e.source_id] = []
                if e.target_id not in adj_list: adj_list[e.target_id] = []
                adj_list[e.source_id].append(e.target_id)
                adj_list[e.target_id].append(e.source_id)
                
            while queue:
                curr_id, curr_depth = queue.popleft()
                if curr_depth < depth:
                    for neighbor in adj_list.get(curr_id, []):
                        if neighbor not in visited_nodes:
                            visited_nodes.add(neighbor)
                            queue.append((neighbor, curr_depth + 1))
                            
            filtered_nodes = [n for n in filtered_nodes if n.id in visited_nodes]

        # Pagination
        paginated_nodes = filtered_nodes[offset:offset+limit]
        paginated_ids = {n.id for n in paginated_nodes}
        
        dto_nodes = []
        for n in paginated_nodes:
            dto_nodes.append(GraphNodeDTO_v1(id=n.id, type=n.node_type.value, attributes=n.properties))
            
        dto_edges = []
        for e in all_edges:
            if e.source_id in paginated_ids and e.target_id in paginated_ids:
                dto_edges.append(GraphEdgeDTO_v1(source=e.source_id, target=e.target_id, type=e.edge_type.value, provenance=str(e.weight)))
                
        return GraphResponseDTO_v1(
            nodes=dto_nodes,
            edges=dto_edges,
            total_nodes=len(filtered_nodes),
            truncated=(offset + limit) < len(filtered_nodes)
        )
