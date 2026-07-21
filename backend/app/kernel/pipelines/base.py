import abc
from typing import List, Optional, Tuple

from app.kernel.models import ExecutionState, PipelineStrategy, CognitiveTopic, Goal


class CognitivePipeline(abc.ABC):
    """
    Abstract base class for all goal-aware cognitive pipelines.
    Every pipeline implements plan, execute, and present.
    """

    @property
    @abc.abstractmethod
    def strategy(self) -> PipelineStrategy:
        """Returns the metadata Strategy that defines this pipeline."""
        pass

    @abc.abstractmethod
    def plan(self, state: ExecutionState) -> ExecutionState:
        """Plans the required capability execution."""
        pass

    @abc.abstractmethod
    def execute(self, state: ExecutionState) -> ExecutionState:
        """Executes the pipeline-specific logic (e.g. Graph, Optimizer, etc)."""
        pass

    @abc.abstractmethod
    def present(self, state: ExecutionState) -> ExecutionState:
        """Presents the findings via the appropriate AnswerBuilder prompt."""
        pass


class PipelineRegistry:
    """Registry to discover and hold pipeline plugins."""
    
    def __init__(self):
        self._pipelines: List[CognitivePipeline] = []

    def register(self, pipeline: CognitivePipeline) -> None:
        """Register a pipeline strategy."""
        self._pipelines.append(pipeline)
        # Sort by priority, highest first
        self._pipelines.sort(key=lambda p: p.strategy.priority, reverse=True)

    def get_all(self) -> List[CognitivePipeline]:
        return self._pipelines

    def resolve(self, topics: Tuple[CognitiveTopic, ...], goals: Tuple[Goal, ...]) -> Optional[CognitivePipeline]:
        """Resolve the best pipeline for the given topics and goals."""
        for pipeline in self._pipelines:
            # Check if pipeline supports the goals (if any are specified)
            supports_goal = False
            if goals:
                supports_goal = any(g in pipeline.strategy.supported_goals for g in goals)
            else:
                supports_goal = True # Default to true if no goals

            # Check if pipeline supports topics
            supports_topic = False
            if topics:
                supports_topic = any(t in pipeline.strategy.supported_topics for t in topics)
            else:
                supports_topic = True

            if supports_goal and supports_topic:
                return pipeline
                
        # Fallback to the first pipeline if nothing matches specifically
        if self._pipelines:
            return self._pipelines[-1] # The lowest priority one, usually informational
            
        return None
