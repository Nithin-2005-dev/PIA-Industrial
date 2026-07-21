from collections import defaultdict

from app.coverage.coverage_report import (
    CoverageReport,
)

from .coverage_policy import (
    CoveragePolicy,
)


class ExpertiseCoveragePolicy(
    CoveragePolicy
):

    THRESHOLD_STRONG = 70.0
    THRESHOLD_MODERATE = 40.0

    def _coverage_multiplier(
        self,
        expert_count: int,
    ) -> float:

        if expert_count == 1:
            return 0.50

        if expert_count == 2:
            return 0.75

        if expert_count == 3:
            return 0.90

        return 1.00

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
        if not module_scores:
            return reports

        # Calculate robust statistics for total expertise across the repository
        import statistics
        all_totals = [sum(scores) for scores in module_scores.values()]
        median_expertise = statistics.median(all_totals)
        
        try:
            q1 = statistics.quantiles(all_totals, n=4)[0]
            q3 = statistics.quantiles(all_totals, n=4)[2]
            iqr = q3 - q1
        except Exception:
            iqr = 0.0
            
        if iqr == 0.0:
            iqr = median_expertise if median_expertise > 0 else 1.0

        for (
            module_id,
            scores,
        ) in module_scores.items():

            expert_count = len(
                scores
            )

            total_expertise = sum(
                scores
            )

            average_expertise = (
                total_expertise
                / expert_count
            )
            
            # Robust scaling: center around median, scale by IQR.
            # E.g. median -> 50, +1 IQR -> 75, -1 IQR -> 25
            z_robust = (total_expertise - median_expertise) / iqr
            
            # Map z_robust to a 0-100 scale using a sigmoid-like or bounded mapping
            # Let's map z_robust=0 to 50, z_robust=1 to 75, z_robust=2 to ~88
            import math
            base_score = 100.0 / (1.0 + math.exp(-z_robust))

            # Multi-signal integration (placeholder for future metrics like documentation/review)
            # Currently relies heavily on expertise with a diversity multiplier
            coverage_score = (
                base_score
                * self._coverage_multiplier(
                    expert_count
                )
            )
            
            # Bound to 0-100
            coverage_score = max(0.0, min(100.0, coverage_score))

            if (
                coverage_score >= self.THRESHOLD_STRONG
            ):
                level = "STRONG"

            elif (
                coverage_score >= self.THRESHOLD_MODERATE
            ):
                level = "MODERATE"

            else:
                level = "WEAK"
                
            # Compute confidence based on expert count (more experts = more confident signal)
            confidence = min(1.0, 0.5 + (expert_count * 0.1))
            uncertainty = 1.0 - confidence

            reports.append(
                CoverageReport(
                    module_ref=(
                        module_refs[
                            module_id
                        ]
                    ),
                    expert_count=(
                        expert_count
                    ),
                    total_expertise=(
                        total_expertise
                    ),
                    coverage_score=(
                        coverage_score
                    ),
                    coverage_uncertainty=uncertainty,
                    coverage_confidence=confidence,
                    coverage_level=(
                        level
                    ),
                )
            )

        reports.sort(
            key=lambda report: (
                report.coverage_score
            ),
            reverse=True,
        )

        return reports