from dataclasses import dataclass


from typing import Optional

@dataclass(frozen=True)
class BenchmarkResult:
    value: float
    percentile: float
    cohort: str
    z_score: Optional[float] = None


class BenchmarkEngine:

    def compare(
        self,
        value: float,
        cohort_values: list[float],
        cohort: str,
        z_score: Optional[float] = None,
    ) -> BenchmarkResult:
        if not cohort_values:
            return BenchmarkResult(
                value=value,
                percentile=0.0,
                cohort=cohort,
                z_score=z_score
            )

        below_or_equal = sum(
            1
            for cohort_value in cohort_values
            if cohort_value <= value
        )

        percentile = below_or_equal / len(
            cohort_values
        )

        return BenchmarkResult(
            value=value,
            percentile=percentile,
            cohort=cohort,
            z_score=z_score
        )


