from .health_projection import (
    HealthProjection,
)

from .trend_service import (
    TrendService,
)


class HistoryService:

    def __init__(
        self,
        projection: HealthProjection,
    ):
        self._projection = projection

        self._trend_service = (
            TrendService()
        )

    def trends(self):

        histories = (
            self._projection
            .all_histories()
        )

        return (
            self._trend_service
            .analyze(
                histories
            )
        )

    def declining(
        self,
        limit: int = 10,
    ):

        histories = (
            self._projection
            .all_histories()
        )

        return (
            self._trend_service
            .declining(
                histories,
                limit,
            )
        )
