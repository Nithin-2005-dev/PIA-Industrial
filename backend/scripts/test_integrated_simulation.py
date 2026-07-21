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

from app.simulation.simulation_service import (
    SimulationService,
)


def main():

    module = EntityRef(
        id="auth.py",
        type=EntityType.FILE,
    )

    owner = EntityRef(
        id="alice",
        type=EntityType.DEVELOPER,
    )

    health_report = HealthReport(
        module_ref=module,
        health_score=80,
        health_level="HEALTHY",
        coverage_score=80,
        concentration_score=0.30,
        bus_factor=4,
    )

    ownership = OwnershipEstimate(
        owner_ref=owner,
        module_ref=module,
        ownership_percentage=0.75,
        effective_score=120,
        ownership_level=(
            OwnershipLevel.PRIMARY
        ),
    )

    result = (
        SimulationService()
        .simulate_departure(
            health_report=health_report,
            ownership_estimate=ownership,
            readiness_score=0.60,
        )
    )

    print(
        "\n=== INTEGRATED SIMULATION ===\n"
    )

    print(
        f"Scenario: "
        f"{result.scenario}"
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