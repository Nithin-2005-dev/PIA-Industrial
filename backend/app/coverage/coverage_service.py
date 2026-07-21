from .coverage_gap import (
    CoverageGap,
)

from .policies.coverage_policy import (
    CoveragePolicy,
)


class CoverageService:

    def __init__(
        self,
        policy: CoveragePolicy,
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

    def top_gaps(
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
                report.coverage_score
            )
        )

        return [
            CoverageGap(
                report=report,
                rank=index + 1,
            )
            for index, report in enumerate(
                reports[:limit]
            )
        ]