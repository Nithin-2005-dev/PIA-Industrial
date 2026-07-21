from __future__ import annotations

from typing import Protocol

from .models import SimulationScenario


class ScenarioProvider(Protocol):
    """Provides a predefined counterfactual scenario."""
    
    @property
    def scenario(self) -> SimulationScenario:
        ...


class SimulationRegistry:
    """Registry for deterministic scenario providers."""
    
    def __init__(self) -> None:
        self._providers: dict[str, ScenarioProvider] = {}
        
    def register(self, provider: ScenarioProvider) -> None:
        self._providers[provider.scenario.name] = provider
        
    def get_all(self) -> tuple[SimulationScenario, ...]:
        return tuple(p.scenario for p in self._providers.values())
        
    def get(self, name: str) -> SimulationScenario | None:
        provider = self._providers.get(name)
        return provider.scenario if provider else None
