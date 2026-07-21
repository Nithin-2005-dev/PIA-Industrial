from typing import List, Tuple
import dataclasses
from .models import ReflectionResult, ExecutionState, AgentMemory
from .provider import LLMProvider

class ReflectionEngine:
    """
    Analyzes Memory and evaluates if more information is required.
    Does NOT rewrite the answer.
    """
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def reflect(self, state: ExecutionState) -> Tuple[ReflectionResult, AgentMemory]:
        """
        Critiques current working memory. Returns ReflectionResult and an updated AgentMemory.
        """
        rm = state.repository_memory
        am = state.agent_memory
        
        if not rm.observations and not rm.facts:
            # Short-circuit if nothing to reflect on
            return ReflectionResult(
                assumptions=(), missing_evidence=(), alternative_explanations=(),
                unsupported_claims=(), contradictions=(), followup_questions=(),
                confidence_delta=0.0, should_replan=True
            ), am
            
        prompt = "Reflect on the current state:\n"
        prompt += "\n# Current Observations\n"
        for obs in rm.observations:
            prompt += f"- {obs.tool}: {obs.output}\n"
            
        response = self.provider.generate(prompt)
        content = response.content.lower()
        
        # Parse the response (naive parser for M57.11)
        should_replan = "should_replan: true" in content or "missing" in content
        missing = []
        if should_replan:
            missing.append("Additional capabilities required to satisfy goal.")
            
        result = ReflectionResult(
            assumptions=(),
            missing_evidence=tuple(missing),
            alternative_explanations=(),
            unsupported_claims=(),
            contradictions=(),
            followup_questions=(),
            confidence_delta=-0.2 if should_replan else 0.1,
            should_replan=should_replan
        )
        
        # Update Agent Memory with missing info
        new_am = dataclasses.replace(am, questions=am.questions + tuple(missing))
        
        return result, new_am
