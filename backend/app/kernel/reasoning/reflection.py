from typing import Any, List
import dataclasses

from app.kernel.graph import GraphEngine, NodeType, EdgeType

@dataclasses.dataclass(frozen=True)
class ReflectionResult:
    is_valid: bool
    missing_evidence: List[str]
    unsupported_inferences: List[str]
    contradictions_found: int

class DeterministicReflectionEngine:
    """
    Reflects on the Reasoning Graph using graph topology, not LLM prompts.
    """
    def __init__(self, graph: GraphEngine):
        self.graph = graph
        
    def reflect(self) -> ReflectionResult:
        unsupported = []
        contradictions = 0
        
        inferences = self.graph.get_all_nodes(NodeType.INFERENCE)
        for inf in inferences:
            # Check if this inference has any SUPPORTS edge pointing to an OBSERVATION
            # If not, it's a hallucination / unsupported.
            support_edges = self.graph.get_edges(inf.id, direction="out", edge_type=EdgeType.SUPPORTS)
            if not support_edges:
                unsupported.append(inf.id)
                
        # Count explicit conflicts
        conflict_nodes = self.graph.get_all_nodes(NodeType.CONFLICT)
        contradictions = len(conflict_nodes)
        
        return ReflectionResult(
            is_valid=(len(unsupported) == 0),
            missing_evidence=[],
            unsupported_inferences=unsupported,
            contradictions_found=contradictions
        )
