from app.concentration.concentration_report import (
    ConcentrationReport,
)

from app.coverage.coverage_report import (
    CoverageReport,
)

from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.executive.executive_recommendation_service import (
    ExecutiveRecommendationService,
)

from app.executive.intervention_cost_service import (
    InterventionCostService,
)

from app.executive.portfolio_optimizer_service import (
    PortfolioOptimizerService,
)

from app.executive.quarterly_planning_service import (
    QuarterlyPlanningService,
)

from app.executive.roadmap_service import (
    RoadmapService,
)

from app.forecasting.forecast_severity import (
    ForecastSeverity,
)

from app.intervention.intervention_impact_service import (
    InterventionImpactService,
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

    plans = (
        QuarterlyPlanningService()
        .create_plan(
            portfolio,
            capacity_per_quarter=2,
        )
    )

    recommendations = (
        ExecutiveRecommendationService()
        .recommend(
            portfolio
        )
    )

    roadmap = (
        RoadmapService()
        .create(
            quarter_plans=plans,
            recommendations=(
                recommendations
            ),
        )
    )

    assert (
        len(
            roadmap.quarter_plans
        )
        == 2
    )

    assert (
        roadmap.recommendations[0]
        .action
        ==
        "Immediate knowledge transfer"
    )

    print(
        "\n=== STRATEGIC ROADMAP ===\n"
    )

    print(
        roadmap.executive_summary
    )

    print(
        "\nQuarter Plans\n"
    )

    for plan in roadmap.quarter_plans:

        print(
            f"Q{plan.quarter}"
        )

        print(
            f"Gain: "
            f"{plan.total_expected_gain:.2f}"
        )

        print(
            f"Cost: "
            f"{plan.total_cost:.2f}"
        )

        print()

        for item in plan.items:

            print(
                f"- {item.action}"
            )

        print(
            "-" * 50
        )


if __name__ == "__main__":
    main()