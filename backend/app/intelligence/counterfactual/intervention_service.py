from .intervention import (
    Intervention,
)


class InterventionService:

    def recommend(
        self,
        coverage_report,
        concentration_report,
        severity_report,
    ):

        interventions = []

        module_ref = (
            coverage_report.module_ref
        )

        if (
            coverage_report.coverage_score
            < 25
        ):

            interventions.append(
                Intervention(
                    module_ref=module_ref,
                    action=(
                        "Train additional experts"
                    ),
                    priority=70,
                    reason=(
                        "Weak expertise coverage"
                    ),
                )
            )

        if (
            concentration_report.concentration_score
            > 0.80
        ):

            interventions.append(
                Intervention(
                    module_ref=module_ref,
                    action=(
                        "Reduce knowledge concentration"
                    ),
                    priority=80,
                    reason=(
                        "High concentration risk"
                    ),
                )
            )

        if (
            severity_report.severity_score
            >= 0.75
        ):

            interventions.append(
                Intervention(
                    module_ref=module_ref,
                    action=(
                        "Immediate knowledge transfer"
                    ),
                    priority=100,
                    reason=(
                        "Extreme forecast severity"
                    ),
                )
            )

        interventions.sort(
            key=lambda intervention: (
                intervention.priority
            ),
            reverse=True,
        )

        return interventions