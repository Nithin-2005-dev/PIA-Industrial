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
        health_level="CRITICAL",
        coverage_score=30,
        concentration_score=0.95,
        bus_factor=1,
    )


def main():

    projection = HealthProjection()

    payments = module(
        "payments.py"
    )

    auth = module(
        "auth.py"
    )

    now = datetime.now(
        UTC
    )

    projection.apply(
        report(
            payments,
            70,
        ),
        now - timedelta(days=60),
    )

    projection.apply(
        report(
            payments,
            50,
        ),
        now - timedelta(days=30),
    )

    projection.apply(
        report(
            payments,
            40,
        ),
        now,
    )

    projection.apply(
        report(
            auth,
            85,
        ),
        now,
    )

    history = projection.history_of(
        "payments.py"
    )

    histories = (
        projection.all_histories()
    )

    assert len(history.snapshots) == 3
    assert history.module_ref.id == "payments.py"
    assert history.snapshots[-1].health_score == 40
    assert len(histories) == 2

    try:
        projection.history_of(
            "missing.py"
        )
    except ValueError as error:
        assert (
            str(error)
            == "No history for missing.py"
        )
    else:
        raise AssertionError(
            "Expected missing history to raise."
        )

    print(
        "\n=== HEALTH PROJECTION ===\n"
    )

    print(
        f"Module: "
        f"{history.module_ref.id}"
    )

    print(
        f"Snapshots: "
        f"{len(history.snapshots)}"
    )

    print(
        f"All Histories: "
        f"{len(histories)}"
    )


if __name__ == "__main__":
    main()
