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

    module = EntityRef(
        id="auth.py",
        type=EntityType.FILE,
    )

    print(
        "\n=== NO SUCCESSOR ===\n"
    )

    result = (
        DeveloperDeparturePolicy()
        .simulate(
            module_ref=module,
            health_score=80,
            ownership_share=0.80,
            readiness_score=0.0,
            developer_name="alice",
        )
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
        f"Severity: "
        f"{result.severity}"
    )

    print(
        "-" * 60
    )

    print(
        "\n=== TRAINED SUCCESSOR ===\n"
    )

    result = (
        DeveloperDeparturePolicy()
        .simulate(
            module_ref=module,
            health_score=80,
            ownership_share=0.80,
            readiness_score=0.75,
            developer_name="alice",
        )
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
        f"Severity: "
        f"{result.severity}"
    )


if __name__ == "__main__":
    main()