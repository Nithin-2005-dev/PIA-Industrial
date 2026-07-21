from typing import List
from app.kernel.reasoning.rule_engine import ReasoningRule
from app.kernel.graph import GraphEngine, GraphNode, NodeType, GraphEdge, EdgeType
from app.intelligence.causal.rules import DocumentationRuleProvider

def wrap_documentation_rules() -> List[ReasoningRule]:
    provider = DocumentationRuleProvider()
    rules = []
    for cr in provider.rules():
        def make_condition(cr):
            def condition(graph: GraphEngine) -> List[GraphNode]:
                matches = []
                for obs in graph.get_all_nodes(NodeType.OBSERVATION):
                    ev_nodes = graph.get_neighbors(obs.id, direction="out", edge_type=EdgeType.DERIVED_FROM)
                    for ev in ev_nodes:
                        if ev.node_type == NodeType.EVIDENCE:
                            raw = ev.properties.get("raw_output", {})
                            if cr.cause_node in raw:
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
                    properties={"insight": f"Detected {cr.effect_node} due to {cr.cause_node}", "direction": cr.direction, "mechanism": cr.mechanism_id},
                    confidence=match.confidence * cr.rule_confidence
                )
                graph.add_node(inference)
                graph.add_edge(GraphEdge(source_id=inference.id, target_id=match.id, edge_type=EdgeType.SUPPORTS, weight=1.0))
            return action

        rules.append(ReasoningRule(
            id=cr.id, name=cr.id, description=cr.description,
            condition=make_condition(cr), action=make_action(cr),
            metadata=type("Metadata", (), {"weight": cr.rule_confidence})()
        ))
    return rules

class DocumentationReasoningProvider:
    @property
    def name(self) -> str: return "documentation"
    def rules(self) -> List[ReasoningRule]: return wrap_documentation_rules()
