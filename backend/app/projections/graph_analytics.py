import networkx as nx
from typing import Dict, Any
from app.infrastructure.database.models import KnowledgeGraphProjectionRecord

class KnowledgeGraphAnalytics:
    def __init__(self, projection: KnowledgeGraphProjectionRecord):
        self.projection = projection
        self._nx_graph = None

    def _get_nx_graph(self) -> nx.Graph:
        if self._nx_graph is None:
            self._nx_graph = nx.Graph()
            for n in self.projection.nodes:
                self._nx_graph.add_node(n["id"], **n.get("attributes", {}))
            for e in self.projection.edges:
                self._nx_graph.add_edge(e["source"], e["target"], type=e.get("type"))
        return self._nx_graph

    def compute_build_time_analytics(self) -> Dict[str, Any]:
        """
        Cheap analytics computed synchronously during the build process.
        """
        G = self._get_nx_graph()
        
        node_count = G.number_of_nodes()
        
        components = nx.number_connected_components(G) if node_count > 0 else 0
        density = nx.density(G)
        
        degrees = [d for n, d in G.degree()]
        avg_degree = sum(degrees) / node_count if node_count > 0 else 0
        
        # Simple degree distribution (bucketed)
        dist = {"0-1": 0, "2-5": 0, "6-10": 0, "11+": 0}
        for d in degrees:
            if d <= 1:
                dist["0-1"] += 1
            elif d <= 5:
                dist["2-5"] += 1
            elif d <= 10:
                dist["6-10"] += 1
            else:
                dist["11+"] += 1
                
        return {
            "components": components,
            "density": density,
            "average_degree": avg_degree,
            "degree_distribution": dist,
            "is_complete": False # indicates background analytics aren't done
        }

    def compute_background_analytics(self) -> Dict[str, Any]:
        """
        Expensive analytics intended to be run in a background worker/job.
        """
        G = self._get_nx_graph()
        
        if G.number_of_nodes() == 0:
            return {"error": "Empty graph"}
            
        if nx.is_connected(G):
            largest_cc = G
        else:
            largest_cc = G.subgraph(max(nx.connected_components(G), key=len)).copy()

        try:
            communities = list(nx.community.greedy_modularity_communities(G))
            num_communities = len(communities)
        except:
            num_communities = 0

        articulation_points = list(nx.articulation_points(G))
        bridges = list(nx.bridges(G))

        try:
            diameter = nx.diameter(largest_cc)
        except:
            diameter = -1

        betweenness = nx.betweenness_centrality(largest_cc)
        closeness = nx.closeness_centrality(largest_cc)
        
        top_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]
        top_closeness = sorted(closeness.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "communities": num_communities,
            "articulation_points_count": len(articulation_points),
            "bridges_count": len(bridges),
            "diameter_of_largest_component": diameter,
            "top_betweenness_centrality": [{"id": k, "score": v} for k, v in top_betweenness],
            "top_closeness_centrality": [{"id": k, "score": v} for k, v in top_closeness],
            "is_complete": True
        }
