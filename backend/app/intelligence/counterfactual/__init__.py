"""Counterfactual Simulation Engine (M54)"""

from .engine import ScenarioComparisonEngine, SimulationEngine
from .interventions import (
    ContributorDepartureIntervention,
    DocumentationImprovementIntervention,
    IncreasedPRVolumeIntervention,
    OwnershipRedistributionIntervention,
    ReducedTestCoverageIntervention,
    RepositorySplitIntervention,
    ReviewBottleneckIntervention,
    ReviewerLossIntervention,
    TeamExpansionIntervention,
)
from .models import (
    ScenarioComparison,
    ScenarioContext,
    ScenarioExecutionResult,
    SimulationAssumption,
    SimulationContext,
    SimulationIntervention,
    SimulationProvenance,
    SimulationScenario,
)
from .registry import ScenarioProvider, SimulationRegistry

__all__ = [
    "SimulationEngine",
    "ScenarioComparisonEngine",
    "SimulationRegistry",
    "ScenarioProvider",
    "SimulationScenario",
    "SimulationAssumption",
    "SimulationIntervention",
    "ScenarioExecutionResult",
    "ScenarioContext",
    "SimulationContext",
    "SimulationProvenance",
    "ScenarioComparison",
    
    # Interventions
    "ContributorDepartureIntervention",
    "OwnershipRedistributionIntervention",
    "DocumentationImprovementIntervention",
    "ReviewerLossIntervention",
    "TeamExpansionIntervention",
    "RepositorySplitIntervention",
    "IncreasedPRVolumeIntervention",
    "ReviewBottleneckIntervention",
    "ReducedTestCoverageIntervention",
]
