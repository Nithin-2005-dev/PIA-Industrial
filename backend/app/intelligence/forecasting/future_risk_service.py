from .future_risk import (
    FutureRisk,
)


class FutureRiskService:

    def analyze(
        self,
        forecasts,
    ):

        risks = []

        for forecast in forecasts:

            risk_score = (

                forecast.current_health

                -

                forecast.predicted_health
            )

            risks.append(
                FutureRisk(
                    module_ref=(
                        forecast.module_ref
                    ),
                    current_health=(
                        forecast.current_health
                    ),
                    predicted_health=(
                        forecast.predicted_health
                    ),
                    risk_score=(
                        risk_score
                    ),
                )
            )

        return risks

    def ranking(
        self,
        forecasts,
        limit: int = 10,
    ):

        risks = (
            self.analyze(
                forecasts
            )
        )

        risks.sort(
            key=lambda risk: (
                risk.risk_score
            ),
            reverse=True,
        )

        return risks[:limit]