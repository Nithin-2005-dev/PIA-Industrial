from .departure_scenario_request import (
    DepartureScenarioRequest,
)

from .departure_scenario_service import (
    DepartureScenarioService,
)

from .intervention_scenario_request import (
    InterventionScenarioRequest,
)

from .intervention_scenario_service import (
    InterventionScenarioService,
)

from .scenario_outcome import (
    ScenarioOutcome,
)

from .strategy_comparison_service import (
    StrategyComparisonService,
)


class StrategyScenarioService:

    def __init__(
        self,
        intelligence_context,
    ):

        self._intelligence = (
            intelligence_context
        )

    def evaluate(
        self,
        request,
    ):

        outcomes = []

        departure_result = (
            DepartureScenarioService(
                self._intelligence
            )
            .evaluate(
                DepartureScenarioRequest(
                    strategy_name=(
                        "Owner Departure"
                    ),
                    module_id=(
                        request.module_id
                    ),
                    departing_owner_id=(
                        request
                        .departing_owner_id
                    ),
                )
            )
        )

        outcomes.append(
            ScenarioOutcome(
                strategy_name=(
                    "Owner Departure"
                ),
                predicted_health=(
                    departure_result
                    .health_after
                ),
                future_risk_score=0.0,
            )
        )

        intervention_outcomes = (
            InterventionScenarioService(
                self._intelligence
            )
            .evaluate(
                InterventionScenarioRequest(
                    strategy_name=(
                        "baseline"
                    ),
                    module_id=(
                        request.module_id
                    ),
                    horizon=(
                        request
                        .horizon
                    ),
                )
            )
        )

        outcomes.extend(
            intervention_outcomes
        )

        return (
            StrategyComparisonService()
            .compare(
                outcomes
            )
        )