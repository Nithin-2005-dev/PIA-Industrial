from typing import Any, Callable, List
import dataclasses
import uuid

from app.kernel.graph import GraphEngine, GraphNode, NodeType, GraphEdge, EdgeType

@dataclasses.dataclass(frozen=True)
class RuleMetadata:
    weight: float = 1.0
    version: str = "1.0"
    ontology_path: str = "general"

@dataclasses.dataclass(frozen=True)
class ReasoningRule:
    id: str
    name: str
    description: str
    metadata: RuleMetadata
    # Condition takes the GraphEngine and returns a list of matching nodes or context dicts
    condition: Callable[[GraphEngine], List[Any]]
    # Action takes the GraphEngine and the match context to produce Inference/RootCause nodes
    action: Callable[[GraphEngine, Any, 'ReasoningRule'], None]

class RuleRegistry:
    """Central repository for rules. Decouples weights and configurations from code."""
    def __init__(self):
        self._rules = {}
        
    def register(self, rule: ReasoningRule):
        self._rules[rule.id] = rule
        
    def get_all(self) -> List[ReasoningRule]:
        return list(self._rules.values())

class RuleEngine:
    """
    Evaluates deterministic rules over the Reasoning Graph.
    Does NOT use LLMs. Pure graph algorithms and logical predicates.
    """
    def __init__(self, graph: GraphEngine, registry: RuleRegistry = None):
        self.graph = graph
        self.registry = registry or RuleRegistry()
        
    def register_rule(self, rule: ReasoningRule):
        self.registry.register(rule)
        
    def execute_all(self):
        """Iterates over rules and applies them to the graph."""
        for rule in self.registry.get_all():
            matches = rule.condition(self.graph)
            for match in matches:
                rule.action(self.graph, match, rule)

# Example Rule Factory
def create_single_point_of_failure_rule() -> ReasoningRule:
    """
    IF BusFactor == 1 AND Ownership == High THEN INFERENCE: Knowledge Concentration Risk
    """
    def condition(graph: GraphEngine) -> List[GraphNode]:
        matches = []
        observations = graph.get_all_nodes(NodeType.OBSERVATION)
        for obs in observations:
            # Graph Traversal: Find Evidence nodes this observation is derived from
            evidence_nodes = graph.get_neighbors(obs.id, direction="out", edge_type=EdgeType.DERIVED_FROM)
            for ev in evidence_nodes:
                if ev.node_type == NodeType.EVIDENCE:
                    raw_output = ev.properties.get("raw_output", {})
                    if hasattr(raw_output, "bus_factors"):
                        for bf in raw_output.bus_factors:
                            if bf.bus_factor <= 1:
                                matches.append(obs)
                                break
                    elif isinstance(raw_output, dict):
                        if "bus_factor" in raw_output and raw_output["bus_factor"] <= 1:
                            matches.append(obs)
                            break
        return matches

    def action(graph: GraphEngine, match: GraphNode, rule: ReasoningRule):
        inference_id = GraphNode.generate_id(NodeType.INFERENCE, semantic_target=match.properties.get("entity", "Unknown"), rule_id=rule.id)
        
        inference = GraphNode(
            id=inference_id,
            node_type=NodeType.INFERENCE,
            properties={"insight": "Single Point of Failure Detected", "risk_level": "High"},
            confidence=match.confidence * rule.metadata.weight
        )
        inference = graph.add_node(inference)
        
        edge = GraphEdge(
            source_id=inference.id,
            target_id=match.id,
            edge_type=EdgeType.SUPPORTS,
            weight=1.0
        )
        graph.add_edge(edge)

    return ReasoningRule(
        id="rule_spof",
        name="Single Point of Failure",
        description="Detects high risk bus factor",
        metadata=RuleMetadata(weight=0.9, version="1.1", ontology_path="risk/operational/spof"),
        condition=condition,
        action=action
    )
