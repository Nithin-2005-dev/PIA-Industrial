from typing import Optional, Tuple

from app.kernel.models import (
    SemanticQuery, GoalGraph, ExecutionComplexity, PipelineCostEstimate,
    CognitiveTopic, Goal
)
from app.kernel.pipelines.base import PipelineRegistry, CognitivePipeline


class PipelinePlanner:
    """
    Evaluates the SemanticQuery and GoalGraph to determine the optimal pipeline.
    """
    def __init__(self, registry: PipelineRegistry):
        self.registry = registry

    def select_pipeline(self, semantic_query: SemanticQuery, goal_graph: GoalGraph) -> CognitivePipeline:
        """
        Selects the pipeline to execute based on topics and goals.
        """
        pipeline = self.registry.resolve(
            topics=tuple(semantic_query.topics),
            goals=tuple(semantic_query.goals)
        )
        if not pipeline:
            # Fallback to the lowest priority if resolving failed completely
            pipelines = self.registry.get_all()
            if pipelines:
                pipeline = pipelines[-1]
            else:
                raise RuntimeError("No pipelines registered in the PipelineRegistry.")
                
        return pipeline

    def estimate_cost(self, pipeline: CognitivePipeline, goal_graph: GoalGraph) -> PipelineCostEstimate:
        """
        Estimates execution cost for the selected pipeline.
        """
        strategy = pipeline.strategy
        
        # Base cost based on complexity
        if strategy.complexity == ExecutionComplexity.SIMPLE:
            latency = 1000.0
            tokens = 1000
            memory = 150.0
        elif strategy.complexity == ExecutionComplexity.MEDIUM:
            latency = 5000.0
            tokens = 4000
            memory = 250.0
        else:
            latency = 15000.0
            tokens = 12000
            memory = 500.0
            
        # Scale by number of goals
        scale = max(1.0, len(goal_graph.nodes) * 0.5)
        
        cost_usd = (tokens / 1000) * 0.01
        
        return PipelineCostEstimate(
            estimated_latency_ms=latency * scale,
            estimated_tokens=int(tokens * scale),
            estimated_memory_mb=memory * scale,
            estimated_cost=cost_usd * scale
        )
