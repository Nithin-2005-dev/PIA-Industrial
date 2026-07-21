from typing import Tuple
from .models import ExecutionGraph, ExecutionNode, CognitiveTopic, CognitiveGoal

class GoalDecomposer:
    """
    Decomposes a top-level CognitiveGoal into a DAG of ExecutionNodes (GoalGraph).
    """
    def decompose(self, goal: CognitiveGoal) -> ExecutionGraph:
        """
        In a full implementation, this uses LLM to decompose the goal.
        For deterministic fast paths and benchmarks, we build it directly based on intent and topics.
        """
        nodes = []
        edges = []
        
        # Simple heuristic mapping for M57.11 to show DAG capability
        if goal.classification:
            topics = goal.classification.topics
            
            # Create a sequence of nodes for the topics
            prev_node_id = None
            
            for i, topic in enumerate(topics):
                node_id = f"subgoal_{i}"
                semantic_goal = f"Resolve {topic.name.lower()} concerns"
                
                node = ExecutionNode(
                    id=node_id,
                    semantic_goal=semantic_goal,
                    dependencies=(prev_node_id,) if prev_node_id else (),
                    required_capabilities=(topic,)
                )
                nodes.append(node)
                
                if prev_node_id:
                    edges.append((prev_node_id, node_id))
                    
                prev_node_id = node_id
                
            if not nodes:
                # Default fallback node
                node = ExecutionNode(
                    id="subgoal_0",
                    semantic_goal=f"Answer: {goal.query}",
                    dependencies=(),
                    required_capabilities=(CognitiveTopic.REPOSITORY,)
                )
                nodes.append(node)

        return ExecutionGraph(nodes=tuple(nodes), edges=tuple(edges))
