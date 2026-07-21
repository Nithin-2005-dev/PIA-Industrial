from .scenario_outcome import (
    ScenarioOutcome,
)


class ScenarioExecutionService:
    """
    M30.1 foundation.

    Later milestones will connect:

    - ForecastPipelineService
    - FutureRiskPipelineService
    - SimulationService
    - Intervention services

    For now this simply creates
    scenario outcomes that can
    be compared.
    """

    def execute(
        self,
        request,
        predicted_health: float,
        future_risk_score: float,
    ):

        return ScenarioOutcome(
            strategy_name=(
                request.strategy_name
            ),
            predicted_health=(
                predicted_health
            ),
            future_risk_score=(
                future_risk_score
            ),
        )