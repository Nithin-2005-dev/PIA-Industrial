from app.knowledge.evidence.ranking.ranking import EvidenceRankingEngine
from app.knowledge.evidence.ranking.ranking import EvidenceRankingPolicy
from app.knowledge.evidence.ranking.ranking import OrganizationalPageRankEngine
from typing import Dict, Any

class RankingService:
    def __init__(self, graph_store: Any):
        # Must implement IEvidenceGraphStore
        self.store = graph_store
        self.pagerank = OrganizationalPageRankEngine()
        
    def execute_global_ranking(self) -> Dict[str, float]:
        """Extracts the graph topology, computes gravity, and updates node authority."""
        # Assuming the interface methods exist
        nodes = self.store.get_all_node_ids()
        edges = self.store.get_all_edges()
        
        # Transform graph edges into the pure mathematical dictionary schema
        formatted_edges = [
            {
                "source": getattr(e, 'source_id', e.get('source_id', None)), 
                "target": getattr(e, 'target_id', e.get('target_id', None)), 
                "type": getattr(e, 'relationship_type', e.get('relationship_type', None)),
                # Bridge the domains: The Measurement Layer Z-Score becomes the edge weight
                "weight": getattr(e, 'measurement_z_score', 1.0)
            } 
            for e in edges
        ]
        
        authority_scores = self.pagerank.calculate_authority(nodes, formatted_edges)
        
        # Persist the Gravity scores back to the nodes for downstream Cognitive Agents
        for node_id, score in authority_scores.items():
            self.store.update_node_property(node_id, "structural_authority", score)
            
        return authority_scores

__all__ = [
    "EvidenceRankingEngine",
    "EvidenceRankingPolicy",
    "OrganizationalPageRankEngine",
    "RankingService",
]

