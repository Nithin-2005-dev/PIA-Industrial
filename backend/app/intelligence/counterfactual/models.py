from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class SimulationAssumption:
    """A human-readable assumption behind a scenario."""
    description: str


class SimulationIntervention(Protocol):
    """An operation to perform on the cloned PlatformContext."""
    name: str
    
    def apply(self, context: Any) -> None:
        """Apply the intervention to the context in-place."""
        ...

    def restart_stage(self) -> str:
        """Indicate which pipeline module must be restarted when this intervention is applied."""
        ...


@dataclass(frozen=True, slots=True)
class SimulationScenario:
    """Represents a single named scenario with interventions and assumptions."""
    name: str
    description: str
    assumptions: tuple[SimulationAssumption, ...]
    interventions: tuple[SimulationIntervention, ...]


@dataclass(frozen=True, slots=True)
class ScenarioExecutionResult:
    """The isolated downstream results produced by a scenario run."""
    org_intelligence: Any | None = None
    reasoning_results: tuple[Any, ...] = ()
    decisions: tuple[Any, ...] = ()
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ScenarioComparison:
    """Delta, Impact Score, Confidence, and Recommendation Priority between baseline and an outcome."""
    baseline_health: float
    scenario_health: float
    health_delta: float
    
    baseline_bus_factor: int
    scenario_bus_factor: int
    bus_factor_delta: int

    baseline_coverage: float
    scenario_coverage: float
    coverage_delta: float
    
    baseline_high_risks: int
    scenario_high_risks: int
    high_risks_delta: int
    
    impact_score: float
    confidence: float
    recommendation_priority: str


@dataclass(frozen=True, slots=True)
class SimulationProvenance:
    """Lineage tracking for simulations."""
    scenario_name: str
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())


@dataclass(slots=True)
class ScenarioContext:
    """
    A wrapper for a scenario containing the cloned state and execution results.
    Not frozen because the runtime populates it.
    """
    scenario: SimulationScenario
    baseline_context: Any  # Reference to original PlatformContext
    cloned_context: Any | None = None  # The branched context
    execution_result: ScenarioExecutionResult | None = None
    comparison: ScenarioComparison | None = None
    provenance: SimulationProvenance | None = None


@dataclass(frozen=True, slots=True)
class SimulationContext:
    """The aggregate result stored in the main PlatformContext, containing all generated scenarios."""
    scenarios: tuple[ScenarioContext, ...]
