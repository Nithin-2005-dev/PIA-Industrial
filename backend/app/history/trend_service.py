from .trend_analyzer import (
    TrendAnalyzer,
)

from .trend_risk import (
    TrendRisk,
)


class TrendService:

    def __init__(self):

        self._analyzer = (
            TrendAnalyzer()
        )

    def analyze(
        self,
        histories,
    ):

        return [
            self._analyzer.analyze(
                history
            )
            for history in histories
        ]

    def declining(
        self,
        histories,
        limit: int = 10,
    ):

        trends = (
            self.analyze(
                histories
            )
        )

        declining = [

            trend

            for trend in trends

            if (
                trend.direction.value
                == "DECLINING"
            )
        ]

        declining.sort(
            key=lambda trend: (
                trend.slope
            )
        )

        return [

            TrendRisk(
                trend=trend,
                rank=index + 1,
            )

            for index, trend in enumerate(
                declining[:limit]
            )
        ]