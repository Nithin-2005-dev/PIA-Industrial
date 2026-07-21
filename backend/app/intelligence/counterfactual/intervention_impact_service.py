from .intervention_impact import (
    InterventionImpact,
)


class InterventionImpactService:

    def estimate(
        self,
        coverage_report,
        concentration_report,
        severity_report,
    ):

        impacts = []

        module_ref = (
            coverage_report.module_ref
        )

        if (
            severity_report.severity_score
            >= 0.75
        ):

            gain = (
                severity_report.severity_score
                * 30
            )

            impacts.append(
                InterventionImpact(
                    module_ref=module_ref,
                    action=(
                        "Immediate knowledge transfer"
                    ),
                    expected_health_gain=(
                        gain
                    ),
                    reason=(
                        "Extreme forecast severity"
                    ),
                )
            )

        if (
            concentration_report.concentration_score
            > 0.80
        ):

            gain = (
                concentration_report
                .concentration_score
                * 20
            )

            impacts.append(
                InterventionImpact(
                    module_ref=module_ref,
                    action=(
                        "Reduce knowledge concentration"
                    ),
                    expected_health_gain=(
                        gain
                    ),
                    reason=(
                        "High concentration risk"
                    ),
                )
            )

        if (
            coverage_report.coverage_score
            < 25
        ):

            gain = (
                (
                    25
                    -
                    coverage_report
                    .coverage_score
                )
                * 0.5
            )

            impacts.append(
                InterventionImpact(
                    module_ref=module_ref,
                    action=(
                        "Train additional experts"
                    ),
                    expected_health_gain=(
                        gain
                    ),
                    reason=(
                        "Weak expertise coverage"
                    ),
                )
            )

        impacts.sort(
            key=lambda impact: (
                impact.expected_health_gain
            ),
            reverse=True,
        )

        return impacts