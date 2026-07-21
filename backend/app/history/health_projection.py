from datetime import datetime

from app.intelligence.assets.health_report import (
    HealthReport,
)

from .health_history import (
    HealthHistory,
)

from .health_snapshot import (
    HealthSnapshot,
)


class HealthProjection:

    def __init__(self):

        self._snapshots: dict[
            str,
            list[HealthSnapshot],
        ] = {}

    def apply(
        self,
        report: HealthReport,
        recorded_at: datetime,
    ) -> HealthSnapshot:

        snapshot = HealthSnapshot(
            module_ref=report.module_ref,
            health_score=report.health_score,
            recorded_at=recorded_at,
        )

        self._snapshots.setdefault(
            report.module_ref.id,
            [],
        ).append(
            snapshot
        )

        return snapshot

    def history_of(
        self,
        module_id: str,
    ) -> HealthHistory:

        snapshots = (
            self._snapshots.get(
                module_id,
                [],
            )
        )

        if not snapshots:

            raise ValueError(
                f"No history for {module_id}"
            )

        return HealthHistory(
            module_ref=(
                snapshots[0]
                .module_ref
            ),
            snapshots=list(
                snapshots
            ),
        )

    def all_histories(
        self,
    ) -> list[HealthHistory]:

        histories = []

        for snapshots in (
            self._snapshots.values()
        ):

            histories.append(
                HealthHistory(
                    module_ref=(
                        snapshots[0]
                        .module_ref
                    ),
                    snapshots=list(
                        snapshots
                    ),
                )
            )

        return histories
