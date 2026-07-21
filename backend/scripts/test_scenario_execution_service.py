from app.scenario.scenario_execution_service import (
    ScenarioExecutionService,
)

from app.scenario.scenario_request import (
    ScenarioRequest,
)

from app.scenario.strategy_comparison_service import (
    StrategyComparisonService,
)


def main():

    service = (
        ScenarioExecutionService()
    )

    baseline = service.execute(
        ScenarioRequest(
            strategy_name=(
                "baseline"
            ),
            module_id=(
                "payments.py"
            ),
        ),
        predicted_health=60,
        future_risk_score=40,
    )

    knowledge_transfer = (
        service.execute(
            ScenarioRequest(
                strategy_name=(
                    "knowledge_transfer"
                ),
                module_id=(
                    "payments.py"
                ),
            ),
            predicted_health=80,
            future_risk_score=20,
        )
    )

    outcomes = (
        StrategyComparisonService()
        .compare(
            [
                baseline,
                knowledge_transfer,
            ]
        )
    )

    assert (
        outcomes[0]
        .strategy_name
        ==
        "knowledge_transfer"
    )

    print(
        "\n=== SCENARIO COMPARISON ===\n"
    )

    for outcome in outcomes:

        print(
            f"Strategy: "
            f"{outcome.strategy_name}"
        )

        print(
            f"Predicted Health: "
            f"{outcome.predicted_health:.2f}"
        )

        print(
            f"Future Risk: "
            f"{outcome.future_risk_score:.2f}"
        )

        print(
            "-" * 50
        )


if __name__ == "__main__":
    main()