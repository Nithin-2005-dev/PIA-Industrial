from .concentration_risk import (
    ConcentrationRisk,
)

from .policies.concentration_policy import (
    ConcentrationPolicy,
)


class ConcentrationService:

    def __init__(
        self,
        policy: ConcentrationPolicy,
    ):
        self._policy = policy

    def analyze(
        self,
        expertise_estimates,
    ):

        return (
            self._policy.analyze(
                expertise_estimates
            )
        )

    def top_risks(
        self,
        expertise_estimates,
        limit: int = 10,
    ):

        reports = (
            self.analyze(
                expertise_estimates
            )
        )

        reports.sort(
            key=lambda report: (
                report.concentration_score
            ),
            reverse=True,
        )

        return [
            ConcentrationRisk(
                report=report,
                rank=index + 1,
            )
            for index, report in enumerate(
                reports[:limit]
            )
        ]