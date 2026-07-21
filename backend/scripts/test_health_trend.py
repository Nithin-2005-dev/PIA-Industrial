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

from app.history.trend_analyzer import (
    TrendAnalyzer,
)


def main():

    module = EntityRef(
        id="auth.py",
        type=EntityType.FILE,
    )

    now = datetime.now(
        UTC
    )

    history = HealthHistory(
        module_ref=module,
        snapshots=[
            HealthSnapshot(
                module_ref=module,
                health_score=92,
                recorded_at=(
                    now
                    - timedelta(days=90)
                ),
            ),
            HealthSnapshot(
                module_ref=module,
                health_score=88,
                recorded_at=(
                    now
                    - timedelta(days=60)
                ),
            ),
            HealthSnapshot(
                module_ref=module,
                health_score=81,
                recorded_at=(
                    now
                    - timedelta(days=30)
                ),
            ),
            HealthSnapshot(
                module_ref=module,
                health_score=80,
                recorded_at=now,
            ),
        ],
    )

    trend = (
        TrendAnalyzer()
        .analyze(
            history
        )
    )

    print(
        "\n=== HEALTH TREND ===\n"
    )

    print(
        f"Module: "
        f"{trend.module_ref.id}"
    )

    print(
        f"First: "
        f"{trend.previous_score:.2f}"
    )

    print(
        f"Current: "
        f"{trend.current_score:.2f}"
    )

    print(
        f"Delta: "
        f"{trend.delta:.2f}"
    )

    print(
        f"Slope: "
        f"{trend.slope:.2f}"
    )

    print(
        f"Direction: "
        f"{trend.direction.value}"
    )


if __name__ == "__main__":
    main()