from .health_risk import (
    HealthRisk,
)

from .policies.health_policy import (
    HealthPolicy,
)


class HealthService:

    def __init__(
        self,
        policy: HealthPolicy,
    ):
        self._policy = policy

    def analyze(
        self,
        coverage_reports,
        concentration_reports,
        bus_factor_reports,
    ):

        return (
            self._policy.evaluate(
                coverage_reports,
                concentration_reports,
                bus_factor_reports,
            )
        )

    def ranking(
        self,
        coverage_reports,
        concentration_reports,
        bus_factor_reports,
        limit: int = 10,
    ):

        reports = (
            self.analyze(
                coverage_reports,
                concentration_reports,
                bus_factor_reports,
            )
        )

        reports.sort(
            key=lambda report: (
                report.health_score
            ),
            reverse=True,
        )

        return [
            HealthRisk(
                report=report,
                rank=index + 1,
            )
            for index, report in enumerate(
                reports[:limit]
            )
        ]