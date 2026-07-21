from typing import List, Tuple, Dict, Any
from .models import (
    CapabilityCandidate, AgentAction, SemanticQuery, GoalGraph,
    ExecutionGraph, ExecutionNode, CognitiveTopic
)
from .registry import CapabilityRegistry

class PlanningEngine:
    """
    DAG-Based Agentic Planner.
    Takes top K CapabilityCandidates and builds an execution sequence
    by resolving requires/produces dependencies.
    """
    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry

    def plan(
        self,
        candidates: Tuple[CapabilityCandidate, ...],
        semantic_query: SemanticQuery,
        goal_graph: GoalGraph | None = None
    ) -> Tuple[List[AgentAction], ExecutionGraph, Dict[str, Any]]:
        actions = []
        diagnostics = {
            "Available Candidates": len(candidates),
            "Goal Nodes": len(goal_graph.nodes) if goal_graph else 0,
            "Decisions": [],
            "Alternative Plans": [],
            "Expected Evidence": []
        }
        
        if not candidates:
            return actions, ExecutionGraph(nodes=()), diagnostics
            
        # We take the top scoring candidates. To allow multi-capability planning,
        # we can accept all candidates that score above a threshold, e.g., 0.5
        # Or simply the top 1 if others are much lower.
        top_score = candidates[0].score
        primary_candidates = [c for c in candidates if c.score >= min(top_score * 0.8, 0.6)]

        # Ensure the plan covers the goal graph, not only the highest scoring
        # neighborhood. A multi-goal question such as "why is ownership
        # concentration risky?" needs ownership, risk, and causal evidence even
        # when one capability dominates lexical similarity.
        covered_goals = {goal for c in primary_candidates for goal in c.satisfied_goals}
        for goal in semantic_query.goals:
            if goal in covered_goals:
                continue
            goal_candidates = [c for c in candidates if goal in c.satisfied_goals and c.available]
            if goal_candidates:
                best = max(goal_candidates, key=lambda c: c.score)
                if best not in primary_candidates:
                    primary_candidates.append(best)
                    covered_goals.add(goal)
        
        if not primary_candidates:
            primary_candidates = [candidates[0]]
            
        diagnostics["Decisions"].append({
            "Satisfied Goals": sorted({g.name for c in primary_candidates for g in c.satisfied_goals}),
            "Reason": "Highest contract-level semantic score after prerequisite and cost checks"
        })
        
        # Build dependency graph
        resolved_sequence = []
        visited = set()
        
        def visit(tool_name: str):
            if tool_name in visited:
                return
            visited.add(tool_name)
            
            card = self.registry.get(tool_name)
            if not card:
                return
                
            # Depth-first search for dependencies
            for req in card.contract.requires:
                producer = self._find_producer(req)
                if producer:
                    visit(producer.name)
                else:
                    diagnostics["Decisions"].append({
                        "Warning": f"Could not find producer for requirement: {req} needed by {tool_name}"
                    })
                    
            resolved_sequence.append(tool_name)
            
        for c in primary_candidates:
            visit(c.card.name)
            
        execution_nodes = []
        execution_edges = []
        previous_node_id = None

        # Build arguments for each action
        for node in resolved_sequence:
            args = {}
            # Map entities to arguments
            for entity in semantic_query.entities:
                args[f"{entity.type.name.lower()}_val"] = entity.value
                
            # Determine reasoning
            reasoning = "Required dependency"
            for c in primary_candidates:
                if c.card.name == node:
                    reasoning = c.why_selected
                    break
                    
            card = self.registry.get(node)
            if card:
                graph_node_id = f"exec_{len(execution_nodes)}"
                execution_nodes.append(ExecutionNode(
                    id=graph_node_id,
                    semantic_goal=self._semantic_goal_for(card, semantic_query),
                    dependencies=(previous_node_id,) if previous_node_id else (),
                    required_capabilities=self._topics_for(card),
                ))
                if previous_node_id:
                    execution_edges.append((previous_node_id, graph_node_id))
                previous_node_id = graph_node_id
                diagnostics["Expected Evidence"].extend(card.contract.produces or card.contract.required_measurements)

            actions.append(AgentAction(
                tool=node,
                arguments=args,
                reasoning=reasoning
            ))
            
        execution_graph = ExecutionGraph(nodes=tuple(execution_nodes), edges=tuple(execution_edges))
        return actions, execution_graph, diagnostics

    def _find_producer(self, requirement: str):
        """Finds a capability in the registry that produces the required metric."""
        for card in self.registry.get_all():
            if requirement in card.contract.produces:
                return card
        return None

    def _semantic_goal_for(self, card, semantic_query: SemanticQuery) -> str:
        if card.contract.supported_goals:
            matching = [g.value for g in semantic_query.goals if g in card.contract.supported_goals]
            if matching:
                return "satisfy " + ", ".join(matching)
        produced = card.contract.produces or card.contract.required_measurements
        if produced:
            return "produce " + ", ".join(produced)
        return card.description

    def _topics_for(self, card) -> Tuple[CognitiveTopic, ...]:
        terms = " ".join([card.name, card.description, *card.tags]).lower()
        topics = []
        mapping = (
            ("forecast", CognitiveTopic.FORECAST),
            ("simulation", CognitiveTopic.SIMULATION),
            ("causal", CognitiveTopic.CAUSAL),
            ("graph", CognitiveTopic.KNOWLEDGE_GRAPH),
            ("expertise", CognitiveTopic.EXPERTISE),
            ("contributor", CognitiveTopic.EXPERTISE),
            ("organization", CognitiveTopic.ORGANIZATION),
            ("ownership", CognitiveTopic.ORGANIZATION),
            ("health", CognitiveTopic.ORGANIZATION),
            ("risk", CognitiveTopic.ORGANIZATION),
        )
        for needle, topic in mapping:
            if needle in terms and topic not in topics:
                topics.append(topic)
        return tuple(topics or [CognitiveTopic.REPOSITORY])
