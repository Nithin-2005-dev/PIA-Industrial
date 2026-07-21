from typing import Any, Dict
import dataclasses
from app.kernel.graph import GraphEngine, GraphNode, NodeType, EdgeType

@dataclasses.dataclass(frozen=True)
class PriorityPolicy:
    weight_severity: float = 0.4
    weight_impact: float = 0.4
    weight_probability: float = 0.2

class PriorityEngine:
    """
    Computes priority scores 0-100 for nodes using deterministic math.
    """
    def __init__(self, graph: GraphEngine, policy: PriorityPolicy = None):
        self.graph = graph
        self.policy = policy or PriorityPolicy()
        
    def calculate_score(self, confidence: float, severity: float, impact: float, evidence_strength: float, contradiction_penalty: float = 0.0, probability: float = 1.0) -> float:
        """
        Priority Score (0-100) = Base × Multiplier × 100
        Base = (Severity * w_sev) + (Impact * w_imp) + (Probability * w_prob)
        Multiplier = Confidence * Evidence Strength * (1 - Contradiction Penalty)
        """
        base = (severity * self.policy.weight_severity) + (impact * self.policy.weight_impact) + (probability * self.policy.weight_probability)
        multiplier = confidence * evidence_strength * (1.0 - contradiction_penalty)
        raw_score = base * multiplier * 100.0
        
        return min(max(raw_score, 0.0), 100.0)
        
    def semantic_bucket(self, score: float) -> str:
        if score >= 80:
            return "Critical"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Medium"
        else:
            return "Low"

    def score_graph_inferences(self):
        """Iterates over INFERENCE nodes and assigns a priority property."""
        inferences = self.graph.get_all_nodes(NodeType.INFERENCE)
        for inf in inferences:
            # Mock calculations for Phase 3 proof of concept
            # A real system would compute severity from ontology and evidence strength from graph topology
            confidence = inf.confidence
            severity = 0.9 if inf.properties.get("risk_level") == "High" else 0.5
            impact = 0.8 # Mocked constant
            
            # Evidence strength: topological count of support edges
            supports = self.graph.get_edges(inf.id, direction="out", edge_type=EdgeType.SUPPORTS)
            evidence_strength = min(len(supports) / 2.0, 1.0) # max 1.0 if >= 2 supports
            
            contradiction_penalty = 0.0
            
            score = self.calculate_score(confidence, severity, impact, evidence_strength, contradiction_penalty)
            inf.properties["priority_score"] = score
            inf.properties["priority_label"] = self.semantic_bucket(score)
