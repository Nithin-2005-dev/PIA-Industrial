from collections import defaultdict

from app.concentration.concentration_report import (
    ConcentrationReport,
)

from .concentration_policy import (
    ConcentrationPolicy,
)


class ExpertiseConcentrationPolicy(
    ConcentrationPolicy
):

    def analyze(
        self,
        expertise_estimates,
    ):

        module_scores = (
            defaultdict(list)
        )

        module_refs = {}

        for estimate in (
            expertise_estimates
        ):

            module_id = (
                estimate
                .module_ref
                .id
            )

            module_scores[
                module_id
            ].append(
                estimate.raw_score
            )

            module_refs[
                module_id
            ] = estimate.module_ref

        reports = []

        for (
            module_id,
            scores,
        ) in module_scores.items():

            total_expertise = (
                sum(scores)
            )

            top_expert_score = (
                max(scores)
            )

            concentration_score = (
                top_expert_score
                / total_expertise
            )

            if (
                concentration_score
                <= 0.40
            ):
                level = "LOW"

            elif (
                concentration_score
                <= 0.70
            ):
                level = "MODERATE"

            else:
                level = "HIGH"

            reports.append(
                ConcentrationReport(
                    module_ref=(
                        module_refs[
                            module_id
                        ]
                    ),
                    expert_count=len(
                        scores
                    ),
                    concentration_score=(
                        concentration_score
                    ),
                    concentration_level=(
                        level
                    ),
                )
            )

        reports.sort(
            key=lambda report: (
                report.concentration_score
            ),
            reverse=True,
        )

        return reports