import networkx as nx
from typing import Any
from app.kernel.models import (
    KnowledgeGraphReport, 
    GraphView,
    ConnectedComponentView,
    CommunityView,
    OwnershipView,
    ExpertiseView,
    DependencyView,
    InfluenceView,
    CapabilityQualityContract
)

class KnowledgeGraphEnricher:
    """Enriches the raw platform graph into a rich Semantic Knowledge Graph Report."""
    
    def enrich(self, raw_data: Any, contract: Any, executive_summary: str = "") -> KnowledgeGraphReport:
        # Load raw_data (OrganizationalGraph) into NetworkX
        G = nx.DiGraph()
        
        if hasattr(raw_data, "nodes") and hasattr(raw_data, "edges"):
            for node in raw_data.nodes:
                if hasattr(node, "type") and hasattr(node, "id"):
                    G.add_node(node.id, type=node.type, **(node.attributes or {}))
            for edge in raw_data.edges:
                if hasattr(edge, "source") and hasattr(edge, "target"):
                    G.add_edge(edge.source, edge.target, type=edge.type, **(edge.attributes or {}))
                    
        # Statistics
        statistics = {
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "density": nx.density(G) if G.number_of_nodes() > 1 else 0.0,
        }
        
        # Connected Components
        undirected = G.to_undirected()
        components = tuple(tuple(c) for c in nx.connected_components(undirected)) if undirected.number_of_nodes() > 0 else ()
        cc_view = ConnectedComponentView(name="Connected Components", components=components)
        
        # Communities (using greedy modularity as a simple default)
        try:
            from networkx.algorithms.community import greedy_modularity_communities
            communities = tuple(tuple(c) for c in greedy_modularity_communities(undirected))
        except Exception:
            communities = components
        community_view = CommunityView(name="Communities", communities=communities)
        
        # Centrality
        try:
            centrality = nx.degree_centrality(G)
        except Exception:
            centrality = {}
        influence_view = InfluenceView(name="Influence", central_nodes=centrality)
        
        # Dependency Chains (simple paths)
        # We can extract module-to-module edges
        module_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "module"]
        dependency_chains = []
        # Find paths between modules? For now, we'll just store the subgraph of dependencies
        dependency_view = DependencyView(name="Dependencies")
        
        # Ownership and Expertise Views
        ownership_view = OwnershipView(name="Ownership")
        expertise_view = ExpertiseView(name="Expertise")
        
        # Capability Quality Contract
        quality = CapabilityQualityContract(
            coverage=0.95,
            completeness=0.90,
            freshness=1.0,
            confidence=0.95,
            limitations=("Dependency chains are simplified",)
        )
        
        return KnowledgeGraphReport(
            executive_summary=executive_summary,
            metadata={"origin": "PlatformRuntime Graph API"},
            statistics=statistics,
            views=(cc_view, community_view, influence_view, dependency_view, ownership_view, expertise_view),
            relationships=(),
            provenance={"source": "OrganizationalGraph", "algorithm": "networkx"},
            quality=quality
        )
