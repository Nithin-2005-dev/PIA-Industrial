from app.concentration.concentration_report import (
    ConcentrationReport,
)

from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.executive.intervention_cost_service import (
    InterventionCostService,
)

from app.forecasting.forecast_severity import (
    ForecastSeverity,
)

from app.coverage.coverage_report import (
    CoverageReport,
)

from app.intervention.intervention_impact_service import (
    InterventionImpactService,
)

from app.executive.intervention_cost_service import (
    InterventionCostService,
)

from app.executive.portfolio_optimizer_service import (
    PortfolioOptimizerService,
)
def module(name):

    return EntityRef(
        id=name,
        type=EntityType.FILE,
    )


def main():

    module_ref = module(
        "payments.py"
    )

    coverage = CoverageReport(
        module_ref=module_ref,
        expert_count=1,
        total_expertise=20,
        coverage_score=10,
        coverage_level="WEAK",
    )

    concentration = (
        ConcentrationReport(
            module_ref=module_ref,
            expert_count=3,
            concentration_score=0.95,
            concentration_level="HIGH",
        )
    )

    severity = ForecastSeverity(
        module_ref=module_ref,
        current_health=40,
        predicted_health=0,
        severity_score=1.0,
        severity_level="EXTREME",
    )

    interventions = (
        InterventionImpactService()
        .estimate(
            coverage_report=coverage,
            concentration_report=(
                concentration
            ),
            severity_report=(
                severity
            ),
        )
    )

    costs = (
        InterventionCostService()
        .estimate(
            interventions
        )
    )

    portfolio = (
        PortfolioOptimizerService()
        .optimize(
            interventions,
            costs,
        )
    )

    assert len(costs) > 0

    print(
        "\n=== INTERVENTION COSTS ===\n"
    )

    for cost in costs:

        print(
            f"Action: "
            f"{cost.action}"
        )

        print(
            f"Cost: "
            f"{cost.estimated_cost:.2f}"
        )

        print(
            "-" * 50
        )

        print(
        "\n=== PORTFOLIO ===\n"
    )

    for item in portfolio:

        print(
            f"#{item.rank}"
        )

        print(
            f"Action: "
            f"{item.action}"
        )

        print(
            f"Gain: "
            f"{item.expected_health_gain:.2f}"
        )

        print(
            f"Cost: "
            f"{item.estimated_cost:.2f}"
        )

        print(
            f"ROI: "
            f"{item.roi:.2f}"
        )

        print(
            "-" * 50
        )
if __name__ == "__main__":
    main()