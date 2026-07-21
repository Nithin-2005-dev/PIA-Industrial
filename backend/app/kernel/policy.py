from typing import Optional
from .models import ExecutionState, AgentPolicy, ReflectionResult

class PolicyEngine:
    """
    The central brain of the Agent Runtime.
    Decides flow control: when to reflect, when to stop, when to replan, etc.
    """
    def __init__(self, agent_policy: AgentPolicy):
        self.policy = agent_policy

    def should_replan(self, state: ExecutionState) -> bool:
        if state.current_iteration >= self.policy.stopping.max_iterations:
            return False
        
        # If planner confidence drops below threshold
        if state.planner_confidence and state.planner_confidence.topic_confidence < 0.6:
            return True
            
        return False

    def should_stop(self, state: ExecutionState) -> bool:
        if state.current_iteration >= self.policy.stopping.max_iterations:
            return True
        return False

    def need_reflection(self, state: ExecutionState) -> bool:
        """Determines if reflection is needed before finalizing."""
        # Check if confidence dropped or if no tool satisfied the goal
        if state.planner_confidence and state.planner_confidence.missing_evidence_probability > 0.4:
            return True
            
        return False

    def should_switch_provider(self, state: ExecutionState, error_count: int) -> bool:
        if error_count >= self.policy.provider.retry_policy:
            return True
        return False

    def should_answer_deterministically(self, state: ExecutionState, all_providers_failed: bool = False) -> bool:
        if all_providers_failed:
            return True
        return False

    def should_refuse(self, state: ExecutionState) -> bool:
        # Refuse malicious or out of bounds requests (not fully implemented)
        return False

    def should_cache(self, state: ExecutionState) -> bool:
        return self.policy.planning.cache_policy

    def evaluate_post_reflection(self, state: ExecutionState, reflection: ReflectionResult) -> bool:
        """Returns True if replanning is needed after reflection."""
        if state.current_iteration >= self.policy.stopping.max_iterations:
            return False
            
        if reflection.should_replan or reflection.confidence_delta < 0:
            return True
            
        return False
