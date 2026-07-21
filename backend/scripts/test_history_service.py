from datetime import UTC
from datetime import datetime
from datetime import timedelta

from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.health.health_report import (
    HealthReport,
)

from app.history.health_projection import (
    HealthProjection,
)

from app.history.history_service import (
    HistoryService,
)


def module(name):

    return EntityRef(
        id=name,
        type=EntityType.FILE,
    )


def report(
    module_ref,
    health_score,
):

    return HealthReport(
        module_ref=module_ref,
        health_score=health_score,
        health_level="WARNING",
        coverage_score=50,
        concentration_score=0.75,
        bus_factor=2,
    )


def apply_history(
    projection,
    module_ref,
    scores,
):

    now = datetime.now(
        UTC
    )

    for index, score in enumerate(
        scores
    ):

        projection.apply(
            report(
                module_ref,
                score,
            ),
            now - timedelta(
                days=(
                    len(scores)
                    - index
                )
                * 30
            ),
        )


def main():

    projection = HealthProjection()

    payments = module(
        "payments.py"
    )

    analytics = module(
        "analytics.py"
    )

    apply_history(
        projection,
        payments,
        [95, 80, 60, 40],
    )

    apply_history(
        projection,
        analytics,
        [60, 70, 80, 90],
    )

    service = HistoryService(
        projection
    )

    trends = service.trends()

    declining = service.declining()

    assert len(trends) == 2
    assert len(declining) == 1
    assert (
        declining[0]
        .trend
        .module_ref
        .id
        == "payments.py"
    )
    assert (
        declining[0]
        .trend
        .direction
        .value
        == "DECLINING"
    )

    print(
        "\n=== HISTORY SERVICE ===\n"
    )

    print(
        f"Module: "
        f"{declining[0].trend.module_ref.id}"
    )

    print(
        f"Direction: "
        f"{declining[0].trend.direction.value}"
    )

    print(
        f"Slope: "
        f"{declining[0].trend.slope:.2f}"
    )


if __name__ == "__main__":
    main()
