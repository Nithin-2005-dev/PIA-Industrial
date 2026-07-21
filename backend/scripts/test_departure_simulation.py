from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.simulation.developer_departure_policy import (
    DeveloperDeparturePolicy,
)


def main():

    result = (
        DeveloperDeparturePolicy()
        .simulate(
            module_ref=EntityRef(
                id="auth.py",
                type=EntityType.FILE,
            ),
            health_score=80,
            ownership_share=0.75,
            developer_name="alice",
        )
    )

    print(
        "\n=== DEPARTURE SIMULATION ===\n"
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
        f"Impact: "
        f"{result.impact:.2f}"
    )

    print(
        f"Severity: "
        f"{result.severity}"
    )


if __name__ == "__main__":
    main()