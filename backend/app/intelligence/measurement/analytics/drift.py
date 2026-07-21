from dataclasses import dataclass

from app.intelligence.measurement.analytics.statistical import StatisticalEngine


@dataclass(frozen=True)
class DriftResult:
    drift_detected: bool
    drift_type: str
    score: float
    threshold: float


class DriftDetectionEngine:

    def __init__(
        self,
    ):
        self._stats = StatisticalEngine()

    def metric_drift(
        self,
        baseline: list[float],
        current: list[float],
        threshold: float = 0.25,
    ) -> DriftResult:
        baseline_mean = self._stats.mean(
            baseline
        )
        current_mean = self._stats.mean(
            current
        )
        scale = max(
            abs(
                baseline_mean
            ),
            1.0,
        )
        score = abs(
            current_mean - baseline_mean
        ) / scale

        return DriftResult(
            drift_detected=score >= threshold,
            drift_type="metric",
            score=score,
            threshold=threshold,
        )

    def distribution_drift(
        self,
        baseline: list[float],
        current: list[float],
        threshold: float = 0.5,
    ) -> DriftResult:
        bins = self._histogram_bins(
            baseline,
            current,
        )

        baseline_hist = self._histogram(
            baseline,
            bins,
        )
        current_hist = self._histogram(
            current,
            bins,
        )
        score = self._stats.kl_divergence(
            current_hist,
            baseline_hist,
        )

        return DriftResult(
            drift_detected=score >= threshold,
            drift_type="distribution",
            score=score,
            threshold=threshold,
        )

    def schema_drift(
        self,
        baseline_keys: set[str],
        current_keys: set[str],
    ) -> DriftResult:
        union = baseline_keys | current_keys

        if not union:
            score = 0.0
        else:
            score = len(
                baseline_keys ^ current_keys
            ) / len(
                union
            )

        return DriftResult(
            drift_detected=score > 0.0,
            drift_type="schema",
            score=score,
            threshold=0.0,
        )

    def _histogram_bins(
        self,
        left: list[float],
        right: list[float],
    ) -> list[float]:
        values = left + right

        if not values:
            return [
                0.0,
                1.0,
            ]

        minimum = min(
            values
        )
        maximum = max(
            values
        )

        if minimum == maximum:
            return [
                minimum,
                maximum + 1.0,
            ]

        step = (
            maximum - minimum
        ) / 10.0

        return [
            minimum + step * index
            for index in range(11)
        ]

    def _histogram(
        self,
        values: list[float],
        bins: list[float],
    ) -> list[float]:
        counts = [
            0.001
            for _ in bins[:-1]
        ]

        for value in values:
            for index in range(
                len(bins) - 1
            ):
                if (
                    bins[index]
                    <= value
                    <= bins[index + 1]
                ):
                    counts[index] += 1.0
                    break

        return counts


