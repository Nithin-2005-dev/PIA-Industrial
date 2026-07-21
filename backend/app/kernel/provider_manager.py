import dataclasses
from typing import List, Optional, Sequence, Any, Dict
from .models import AgentPolicy
from .provider import LLMProvider, LLMResponse
from .events import get_event_bus

@dataclasses.dataclass(frozen=True)
class ProviderScore:
    availability: float
    latency: float
    quota: float
    cost: float
    health: float
    context: int
    streaming: bool
    reasoning: bool
    json: bool
    embeddings: bool
    function_calling: bool

class ScoredProvider(LLMProvider):
    def __init__(self, provider: LLMProvider, score: ProviderScore):
        self._provider = provider
        self.score = score
        
    def generate(self, prompt: str, tools: Sequence[Any] = ()) -> LLMResponse:
        return self._provider.generate(prompt, tools)

class ProviderManager(LLMProvider):
    """
    Policy-based multi-provider router.
    Handles health checks, quota limits, and seamless failovers using ProviderScore.
    """
    def __init__(self, providers: List[LLMProvider], policy: AgentPolicy):
        self.providers = []
        # Assign mock capabilities to providers
        for p in providers:
            # We mock the ProviderScore for now based on the provider type
            if type(p).__name__ == "MockLLMProvider":
                score = ProviderScore(1.0, 10.0, 1.0, 0.0, 1.0, 100000, False, False, True, False, True)
            else:
                score = ProviderScore(1.0, 500.0, 1.0, 0.5, 1.0, 1000000, True, True, True, True, True)
            self.providers.append(ScoredProvider(p, score))
            
        self.policy = policy
        self.event_bus = get_event_bus()

    def _rank_providers(self, requirements: Dict[str, Any]) -> List[ScoredProvider]:
        """Rank providers mathematically based on constraints."""
        scored_list = []
        for p in self.providers:
            score = 0.0
            
            # Constraints
            if requirements.get("json", False) and not p.score.json:
                continue
            if requirements.get("streaming", False) and not p.score.streaming:
                continue
            if requirements.get("reasoning", False) and not p.score.reasoning:
                continue
            if requirements.get("context", 0) > p.score.context:
                continue
                
            # Scoring
            score += p.score.health * 10
            score += p.score.availability * 5
            score += p.score.quota * 2
            score -= (p.score.cost * 0.1)
            score -= (p.score.latency * 0.001)
            
            scored_list.append((score, p))
            
        # Sort descending by score
        scored_list.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored_list]

    def generate(self, prompt: str, tools: Sequence[Any] = (), requirements: Dict[str, Any] = None) -> LLMResponse:
        if requirements is None:
            requirements = {}
            
        ranked_providers = self._rank_providers(requirements)
        last_error = "No providers available matching requirements."
        
        if not ranked_providers:
            return LLMResponse(content=f"[ALL_PROVIDERS_FAILED]\n{last_error}")
            
        for p in ranked_providers:
            provider_name = type(p._provider).__name__
            self.event_bus.publish("ProviderStarted", "provider", provider=provider_name)
            
            try:
                response = p.generate(prompt, tools)
                
                if "[PROVIDER_ERROR]" in response.content:
                    last_error = response.content
                    self.event_bus.publish("ProviderFailover", "provider", provider=provider_name, error=last_error)
                    continue 
                    
                self.event_bus.publish("ProviderFinished", "provider", provider=provider_name, status="SUCCESS")
                return response
                
            except Exception as e:
                last_error = f"Exception in {provider_name}: {str(e)}"
                self.event_bus.publish("ProviderFailover", "provider", provider=provider_name, error=last_error)
                continue 

        return LLMResponse(content=f"[ALL_PROVIDERS_FAILED]\n{last_error}")
