from __future__ import annotations

from app.intelligence.counterfactual.interventions import (
    ContributorDepartureIntervention,
    DocumentationImprovementIntervention,
    IncreasedPRVolumeIntervention,
    OwnershipRedistributionIntervention,
    ReducedTestCoverageIntervention,
    RepositorySplitIntervention,
    ReviewBottleneckIntervention,
    ReviewerLossIntervention,
    SimulationIntervention,
    TeamExpansionIntervention,
)


class CostModel:
    """
    Estimates the cost of an intervention (e.g., in developer-days or abstract resource units).
    """

    def estimate(self, intervention: SimulationIntervention) -> float:
        # Later, these could be learned values based on historical data.
        if isinstance(intervention, OwnershipRedistributionIntervention):
            return 3.0  # 3 developer-days for knowledge transfer and review
        elif isinstance(intervention, DocumentationImprovementIntervention):
            return 5.0  # 5 developer-days for a documentation sprint
        elif isinstance(intervention, TeamExpansionIntervention):
            return 30.0  # 30 developer-days to hire and onboard
        elif isinstance(intervention, RepositorySplitIntervention):
            return 45.0  # 45 developer-days to split architectures
        elif isinstance(intervention, ContributorDepartureIntervention):
            return 0.0  # Happens to us, no explicit "cost" to trigger, but has negative ROI
        elif isinstance(intervention, ReviewerLossIntervention):
            return 0.0
        elif isinstance(intervention, IncreasedPRVolumeIntervention):
            return 0.0
        elif isinstance(intervention, ReviewBottleneckIntervention):
            return 0.0
        elif isinstance(intervention, ReducedTestCoverageIntervention):
            return 0.0
        
        # Default cost for unknown interventions
        return 1.0
