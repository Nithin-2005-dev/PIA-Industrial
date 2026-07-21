from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.health.health_report import (
    HealthReport,
)

from app.ownership.ownership_estimate import (
    OwnershipEstimate,
)

from app.ownership.ownership_level import (
    OwnershipLevel,
)

from app.simulation.simulation_engine import (
    SimulationEngine,
)

from app.simulation.simulation_scenario import (
    SimulationScenario,
)


def main():

    module = EntityRef(
        id="auth.py",
        type=EntityType.FILE,
    )

    scenario = (
        SimulationScenario(
            module_ref=module,
            departing_owner="alice",
        )
    )

    health_report = (
        HealthReport(
            module_ref=module,
            health_score=80,
            health_level="HEALTHY",
            coverage_score=80,
            concentration_score=0.30,
            bus_factor=4,
        )
    )

    ownership = (
        OwnershipEstimate(
            owner_ref=EntityRef(
                id="alice",
                type=EntityType.DEVELOPER,
            ),
            module_ref=module,
            ownership_percentage=0.75,
            effective_score=120,
            ownership_level=(
                OwnershipLevel.PRIMARY
            ),
        )
    )

    result = (
        SimulationEngine()
        .simulate(
            scenario=scenario,
            health_report=health_report,
            ownership_estimate=ownership,
            readiness_score=0.60,
        )
    )

    print(
        "\n=== SIMULATION ENGINE ===\n"
    )

    print(
        f"Scenario: "
        f"{scenario.departing_owner} leaves"
    )

    print(
        f"Module: "
        f"{result.module_ref.id}"
    )

    print(
        f"Health Before: "
        f"{result.health_before:.2f}"
    )

    print(
        f"Health After: "
        f"{result.health_after:.2f}"
    )

    print(
        f"Knowledge Loss: "
        f"{result.knowledge_loss:.2f}"
    )

    print(
        f"Impact: "
        f"{result.impact:.2f}"
    )

    print(
        f"Severity: "
        f"{result.severity}"
    )


if __name__ == "__main__":
    main()