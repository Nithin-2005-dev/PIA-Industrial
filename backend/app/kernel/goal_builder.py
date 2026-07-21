import uuid
from typing import Tuple, List
from .models import SemanticQuery, GoalGraph, GoalNode, ExecutionNodeState, Goal

class GoalGraphBuilder:
    def __init__(self):
        pass
        
    def build(self, semantic_query: SemanticQuery) -> GoalGraph:
        """
        Converts a SemanticQuery (which may contain multiple sequential goals)
        into a directed acyclic GoalGraph (DAG) for execution.
        """
        nodes = []
        edges = []
        dependencies = {}
        
        # If there are no goals, return an empty graph
        if not semantic_query.goals or semantic_query.goals == [Goal.UNKNOWN]:
            return GoalGraph(nodes=tuple(nodes), edges=tuple(edges), dependencies=dependencies)
            
        previous_node_id = None
        
        for idx, goal in enumerate(semantic_query.goals):
            node_id = f"goal_{idx}_{str(uuid.uuid4())[:8]}"
            
            # Simple assumption: goals form a sequential chain from the user's sentence.
            # In a more advanced implementation, the LLM parser could output true DAG edges.
            node_deps = [previous_node_id] if previous_node_id else []
            if previous_node_id:
                edges.append((previous_node_id, node_id))
                dependencies[node_id] = node_deps
                
            node = GoalNode(
                id=node_id,
                goal=goal,
                inputs=semantic_query.entities, # Pass the resolved entities forward
                outputs=[f"{goal.name}_result"],
                success_criteria=[f"Successfully executed {goal.name}"],
                dependencies=node_deps,
                status=ExecutionNodeState.PENDING,
                confidence=semantic_query.parser_confidence.overall if semantic_query.parser_confidence else 1.0
            )
            nodes.append(node)
            previous_node_id = node_id
            
        return GoalGraph(
            nodes=tuple(nodes),
            edges=tuple(edges),
            dependencies=dependencies
        )
