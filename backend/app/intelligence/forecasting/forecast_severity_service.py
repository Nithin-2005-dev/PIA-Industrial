from .forecast_severity import (
    ForecastSeverity,
)


class ForecastSeverityService:

    def analyze(
        self,
        forecasts,
    ):

        results = []

        for forecast in forecasts:

            if forecast.current_health <= 0:

                severity = 0

            else:

                severity = (

                    forecast.current_health

                    -

                    forecast.predicted_health

                ) / forecast.current_health

            if severity >= 0.75:

                level = "EXTREME"

            elif severity >= 0.50:

                level = "HIGH"

            elif severity >= 0.25:

                level = "MODERATE"

            else:

                level = "LOW"

            results.append(
                ForecastSeverity(
                    module_ref=(
                        forecast.module_ref
                    ),
                    current_health=(
                        forecast.current_health
                    ),
                    predicted_health=(
                        forecast.predicted_health
                    ),
                    severity_score=severity,
                    severity_level=level,
                )
            )

        return results

    def ranking(
        self,
        forecasts,
        limit: int = 10,
    ):

        severities = (
            self.analyze(
                forecasts
            )
        )

        severities.sort(
            key=lambda severity: (
                severity.severity_score
            ),
            reverse=True,
        )

        return severities[:limit]