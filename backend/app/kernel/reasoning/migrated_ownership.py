from typing import List
from app.kernel.reasoning.rule_engine import ReasoningRule
from app.kernel.graph import GraphEngine, GraphNode, NodeType, GraphEdge, EdgeType
from app.intelligence.causal.rules import OwnershipRuleProvider

# Re-use the wrapper logic from the validation suite to wrap the legacy causal rules
def wrap_ownership_rules() -> List[ReasoningRule]:
    provider = OwnershipRuleProvider()
    rules = []
    
    for causal_rule in provider.rules():
        def make_condition(cr):
            def condition(graph: GraphEngine) -> List[GraphNode]:
                matches = []
                for obs in graph.get_all_nodes(NodeType.OBSERVATION):
                    ev_nodes = graph.get_neighbors(obs.id, direction="out", edge_type=EdgeType.DERIVED_FROM)
                    for ev in ev_nodes:
                        if ev.node_type == NodeType.EVIDENCE:
                            raw = ev.properties.get("raw_output", {})
                            if cr.cause_node in raw:
                                # For "increase" rule logic: > 0.5 triggers it
                                val = raw[cr.cause_node]
                                if cr.direction == "increase" and val > 0.5:
                                    matches.append(obs)
                                    break
                                elif cr.direction == "decrease" and val < 0.5:
                                    matches.append(obs)
                                    break
                return matches
            return condition

        def make_action(cr):
            def action(graph: GraphEngine, match: GraphNode, rule: ReasoningRule):
                inference = GraphNode(
                    id=f"inf_{match.id}_{cr.effect_node}",
                    node_type=NodeType.INFERENCE,
                    properties={
                        "insight": f"Detected {cr.effect_node} due to {cr.cause_node}",
                        "direction": cr.direction,
                        "mechanism": cr.mechanism_id
                    },
                    confidence=match.confidence * cr.rule_confidence
                )
                graph.add_node(inference)
                graph.add_edge(GraphEdge(
                    source_id=inference.id, target_id=match.id, edge_type=EdgeType.SUPPORTS, weight=1.0
                ))
            return action

        rr = ReasoningRule(
            id=causal_rule.id,
            name=causal_rule.id,
            description=causal_rule.description,
            condition=make_condition(causal_rule),
            action=make_action(causal_rule),
            metadata=type("Metadata", (), {"weight": causal_rule.rule_confidence})()
        )
        rules.append(rr)
        
    return rules

class OwnershipReasoningProvider:
    @property
    def name(self) -> str:
        return "ownership"
        
    def rules(self) -> List[ReasoningRule]:
        return wrap_ownership_rules()
