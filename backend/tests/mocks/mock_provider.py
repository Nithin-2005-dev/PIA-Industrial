from typing import Sequence
from app.kernel.models import AgentAction
from app.kernel.provider import LLMResponse

class MockLLMProvider:
    """A deterministic mock LLM for testing without API keys."""
    
    def __init__(self, fixed_responses: dict[str, str] = None):
        self.fixed_responses = fixed_responses or {}
        self.call_history = []

    def generate(
        self,
        prompt: str,
        tools: Sequence = (),
    ) -> LLMResponse:
        self.call_history.append({"prompt": prompt, "tools": tools})
        
        # Determine if we're in an agent loop by checking if tools are provided and it's not a critique
        if tools and "critique" not in prompt.lower() and "unsupported claims" not in prompt.lower():
            # Basic deterministic mock agent
            if "Who is the top contributor?" in prompt and "TopContributorsTool" not in prompt:
                return LLMResponse("", actions=[AgentAction("TopContributorsTool", {"top_k": 5}, "Need contributors.")])
            elif "Who is the top contributor?" in prompt and "TopContributorsTool" in prompt and "OwnershipTool" not in prompt:
                return LLMResponse("", actions=[AgentAction("OwnershipTool", {}, "Need ownership data.")])
            elif "Who is the top contributor?" in prompt and "OwnershipTool" in prompt:
                return LLMResponse("Based on the observations, Dev A is the top contributor.", actions=[])
                
            if "Critical modules?" in prompt and "HealthTool" not in prompt:
                return LLMResponse("", actions=[AgentAction("HealthTool", {}, "Need health.")])
            elif "Critical modules?" in prompt and "HealthTool" in prompt:
                return LLMResponse("Critical modules are healthy.", actions=[])
                
            # Default generic mock tool call if it looks like a repository query but not explicitly handled
            if "facebook/react" in prompt and "Observation" not in prompt:
                return LLMResponse("", actions=[AgentAction("OwnershipTool", {}, "Start with ownership.")])
                
        if "plan" in prompt.lower() and ("tool" in prompt.lower() or "capabilit" in prompt.lower()):
            return LLMResponse(content="PLAN: [forecast, causal, organization]")
            
        if "critique" in prompt.lower() or "analyze this text for unsupported claims" in prompt.lower():
            if "hallucination" in prompt.lower() or "[UNVERIFIED CLAIM TO BE REMOVED]" in prompt:
                return LLMResponse(content="CRITIQUE: CLAIM='[UNVERIFIED CLAIM TO BE REMOVED]' SUPPORTED=False REASON='No evidence'")
            return LLMResponse(content="CRITIQUE: CLAIM='valid' SUPPORTED=True REASON='Evidence found'")
            
        # Default fallback
        for key, value in self.fixed_responses.items():
            if key in prompt:
                return LLMResponse(content=value)
                
        return LLMResponse(content="This is a deterministic mock response from the AI Engineering Advisor.")
