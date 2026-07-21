from datetime import UTC
from datetime import datetime
from datetime import timedelta

from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.history.health_history import (
    HealthHistory,
)

from app.history.health_snapshot import (
    HealthSnapshot,
)

from app.history.trend_service import (
    TrendService,
)


def history(
    module_name,
    scores,
):

    module = EntityRef(
        id=module_name,
        type=EntityType.FILE,
    )

    now = datetime.now(
        UTC
    )

    snapshots = []

    for index, score in enumerate(
        scores
    ):

        snapshots.append(
            HealthSnapshot(
                module_ref=module,
                health_score=score,
                recorded_at=(
                    now
                    - timedelta(
                        days=(
                            len(scores)
                            - index
                        )
                        * 30
                    )
                ),
            )
        )

    return HealthHistory(
        module_ref=module,
        snapshots=snapshots,
    )


def main():

    histories = [

        history(
            "payments.py",
            [95, 80, 60, 40],
        ),

        history(
            "auth.py",
            [92, 88, 81, 80],
        ),

        history(
            "analytics.py",
            [60, 70, 80, 90],
        ),
    ]

    rankings = (
        TrendService()
        .declining(
            histories
        )
    )

    print(
        "\n=== DECLINING MODULES ===\n"
    )

    for item in rankings:

        trend = item.trend

        print(
            f"Rank #{item.rank}"
        )

        print(
            f"Module: "
            f"{trend.module_ref.id}"
        )

        print(
            f"Slope: "
            f"{trend.slope:.2f}"
        )

        print(
            f"Direction: "
            f"{trend.direction.value}"
        )

        print(
            "-" * 60
        )


if __name__ == "__main__":
    main()