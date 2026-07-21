from dataclasses import dataclass

from app.knowledge.evidence.domain import Evidence


@dataclass(frozen=True)
class EvidenceRankingPolicy:
    confidence_weight: float = 0.25
    severity_weight: float = 0.2
    business_impact_weight: float = 0.15
    architectural_impact_weight: float = 0.1
    security_impact_weight: float = 0.1
    operational_impact_weight: float = 0.1
    urgency_weight: float = 0.05
    novelty_weight: float = 0.025
    persistence_weight: float = 0.025


class EvidenceRankingEngine:

    def __init__(
        self,
        policy: EvidenceRankingPolicy | None = None,
    ):
        self._policy = policy or EvidenceRankingPolicy()

    def score(
        self,
        evidence: Evidence,
    ) -> float:
        metadata = evidence.metadata

        business_impact = float(
            metadata.get(
                "business_impact",
                evidence.severity.rank() / 4.0,
            )
        )
        architectural_impact = float(
            metadata.get(
                "architectural_impact",
                1.0 if evidence.category == "architecture" else 0.5,
            )
        )
        security_impact = float(
            metadata.get(
                "security_impact",
                1.0 if evidence.category == "security" else 0.0,
            )
        )
        operational_impact = float(
            metadata.get(
                "operational_impact",
                1.0
                if evidence.category == "operational_risk"
                else 0.5,
            )
        )

        return (
            evidence.confidence * self._policy.confidence_weight
            + (evidence.severity.rank() / 4.0)
            * self._policy.severity_weight
            + business_impact
            * self._policy.business_impact_weight
            + architectural_impact
            * self._policy.architectural_impact_weight
            + security_impact
            * self._policy.security_impact_weight
            + operational_impact
            * self._policy.operational_impact_weight
            + (evidence.priority.rank() / 3.0)
            * self._policy.urgency_weight
            + evidence.historical_context.novelty
            * self._policy.novelty_weight
            + evidence.historical_context.persistence
            * self._policy.persistence_weight
        )

    def rank(
        self,
        evidence: tuple[Evidence, ...],
    ) -> tuple[Evidence, ...]:
        return tuple(
            sorted(
                evidence,
                key=self.score,
                reverse=True,
            )
        )


import logging
from typing import Dict, List, Any, Set

logger = logging.getLogger(__name__)

class OrganizationalPageRankEngine:
    # Edges that push the random walker AWAY from the source node
    DESTRUCTIVE_EDGES: Set[str] = {
        'INTRODUCED_BUG_IN', 'CAUSED_INCIDENT', 'BROKE_BUILD', 'REVERTED'
    }
    
    # Edges where the target is a dependency of the source, so gravity flows to target
    DEPENDENCY_EDGES: Set[str] = {
        'DEPENDS_ON', 'CALLS', 'IMPORTS', 'USES'
    }

    def __init__(self, damping_factor: float = 0.85, max_iterations: int = 100, tolerance: float = 1e-6):
        self.damping_factor = damping_factor
        self.max_iterations = max_iterations
        self.tolerance = tolerance

    def calculate_authority(self, nodes: List[str], edges: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculates the Eigenvector Centrality (PageRank) of all nodes in the graph.
        edges payload expected: [{'source': 'node_A', 'target': 'node_B', 'weight': 1.5, 'type': 'AUTHORED'}]
        """
        num_nodes = len(nodes)
        if num_nodes == 0:
            return {}

        ranks = {node: 1.0 / num_nodes for node in nodes}
        incoming_links = {node: [] for node in nodes}
        out_degree_weights = {node: 0.0 for node in nodes}
        
        # 1. Topological Transformation
        for edge in edges:
            src, tgt = edge['source'], edge['target']
            edge_type = edge.get('type', '')
            
            # Extract the pure Z-Score weight from the Measurement Layer
            weight = max(0.001, float(edge.get('weight', 1.0)))
            
            if src in nodes and tgt in nodes:
                if edge_type in self.DESTRUCTIVE_EDGES or edge_type in self.DEPENDENCY_EDGES:
                    # TRAP FIX: Dynamic Topological Inversion / Dependency Flow. 
                    # If Dev causes incident in Router, the link flows FROM Dev TO Router, 
                    # pulling gravity away from the Dev. 
                    # Similarly, if CSS depends on Router, gravity flows FROM CSS to Router.
                    incoming_links[tgt].append((src, weight))
                    out_degree_weights[src] += weight
                else:
                    # Standard Constructive Flow
                    # If Dev authored Router, gravity flows from Router to Dev.
                    incoming_links[src].append((tgt, weight))
                    out_degree_weights[tgt] += weight

        # 2. Power Iteration (The Markov Random Walk)
        for iteration in range(self.max_iterations):
            new_ranks = {}
            max_diff = 0.0
            
            teleport_prob = (1.0 - self.damping_factor) / num_nodes
            
            for node in nodes:
                rank_sum = 0.0
                for source, weight in incoming_links[node]:
                    if out_degree_weights[source] > 0:
                        rank_sum += ranks[source] * (weight / out_degree_weights[source])
                
                new_ranks[node] = teleport_prob + (self.damping_factor * rank_sum)
                max_diff = max(max_diff, abs(new_ranks[node] - ranks[node]))
                
            ranks = new_ranks
            
            if max_diff < self.tolerance:
                logger.info(f"Engineering PageRank converged after {iteration + 1} iterations.")
                break
                
        return ranks

