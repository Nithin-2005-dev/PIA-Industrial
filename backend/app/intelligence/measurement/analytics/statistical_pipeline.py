from dataclasses import dataclass

from app.intelligence.measurement.analytics.outliers import OutlierDetectionEngine
from app.intelligence.measurement.analytics.statistical import StatisticalEngine


from typing import Optional

@dataclass(frozen=True)
class StatisticalReport:
    mean: Optional[float]
    median: Optional[float]
    variance: Optional[float]
    outlier_indices: tuple[int, ...]
    confidence_interval: Optional[tuple[float, float]]
    distribution: str
    z_score: Optional[float] = None


class StatisticsPipeline:

    def __init__(
        self,
    ):
        self._stats = StatisticalEngine()
        self._outliers = OutlierDetectionEngine()

    def _windsorize(self, values: list[float], percentile: float = 0.05) -> list[float]:
        """
        Clips extreme outliers from the population to prevent baseline contamination.
        Example: percentile=0.05 clips the top 5% and bottom 5% of values.
        """
        if not values or len(values) < 5:
            return values # Not enough data to windsorize
            
        sorted_vals = sorted(values)
        clip_count = int(len(sorted_vals) * percentile)
        
        if clip_count == 0:
            return sorted_vals
            
        # Replace the extremes with the boundary values (clipping)
        lower_bound = sorted_vals[clip_count]
        upper_bound = sorted_vals[-(clip_count + 1)]
        
        windsorized = []
        for v in values:
            if v < lower_bound:
                windsorized.append(lower_bound)
            elif v > upper_bound:
                windsorized.append(upper_bound)
            else:
                windsorized.append(v)
                
        return windsorized

    def analyze(
        self,
        values: list[float],
        target_value: Optional[float] = None,
    ) -> StatisticalReport:
        """
        Analyzes a population. If target_value is provided, calculates its Z-Score 
        against the windsorized historical baseline.
        """
        if not values:
            return StatisticalReport(
                mean=None, median=None, variance=None, outlier_indices=(),
                confidence_interval=None, distribution="unknown", z_score=None
            )

        # 1. Sanitize the Baseline
        clean_values = self._windsorize(values)
        
        # 2. Calculate the True Baseline
        clean_mean = self._stats.mean(clean_values)
        variance = self._stats.variance(clean_values)
        safe_deviation = self._stats.calculate_safe_deviation(clean_values)
        
        confidence_interval = None
        if variance is not None and clean_mean is not None:
            count = len(clean_values)
            if count > 0:
                margin = 1.96 * safe_deviation / (count ** 0.5)
            else:
                margin = 0.0
            confidence_interval = (
                clean_mean - margin,
                clean_mean + margin,
            )

        # 3. Calculate Z-Score for the current target (if provided)
        z_score = None
        if target_value is not None and clean_mean is not None:
            z_score = (target_value - clean_mean) / safe_deviation

        return StatisticalReport(
            mean=clean_mean,
            median=self._stats.median(clean_values),
            variance=variance,
            outlier_indices=tuple(self._outliers.mad_outliers(values)),
            confidence_interval=confidence_interval,
            distribution=self._distribution(clean_values),
            z_score=z_score,
        )

    def _distribution(
        self,
        values: list[float],
    ) -> str:
        if len(
            values
        ) < 3:
            return "unknown"

        average = self._stats.mean(
            values
        )
        median = self._stats.median(
            values
        )

        if average is None or median is None:
            return "unknown"

        if abs(
            average - median
        ) <= max(
            1.0,
            abs(average),
        ) * 0.05:
            return "approximately_symmetric"

        if average > median:
            return "right_skewed"

        return "left_skewed"


