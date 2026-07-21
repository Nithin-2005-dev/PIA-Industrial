from math import log2
from statistics import mean
from statistics import median
from typing import Optional


import math

class StatisticalEngine:
    MINIMUM_VARIANCE_FLOOR = 0.01 

    def calculate_safe_deviation(self, windsorized_values: list[float]) -> float:
        """Calculates standard deviation with a regularization floor."""
        var = self.variance(windsorized_values)
        if var is None or var < self.MINIMUM_VARIANCE_FLOOR:
            return math.sqrt(self.MINIMUM_VARIANCE_FLOOR)
        return math.sqrt(var)

    def mean(
        self,
        values: list[float],
    ) -> Optional[float]:
        return mean(
            values
        ) if values else None

    def median(
        self,
        values: list[float],
    ) -> Optional[float]:
        return median(
            values
        ) if values else None

    def variance(
        self,
        values: list[float],
    ) -> Optional[float]:
        if len(
            values
        ) < 2:
            return None

        average = mean(
            values
        )

        return sum(
            (
                value - average
            )
            ** 2
            for value in values
        ) / (
            len(
                values
            )
            - 1
        )

    def covariance(
        self,
        left: list[float],
        right: list[float],
    ) -> Optional[float]:
        count = min(
            len(left),
            len(right),
        )

        if count < 2:
            return None

        left_values = left[:count]
        right_values = right[:count]
        left_mean = mean(
            left_values
        )
        right_mean = mean(
            right_values
        )

        return sum(
            (
                left_values[index]
                - left_mean
            )
            * (
                right_values[index]
                - right_mean
            )
            for index in range(count)
        ) / (count - 1)

    def correlation(
        self,
        left: list[float],
        right: list[float],
    ) -> Optional[float]:
        covariance = self.covariance(
            left,
            right,
        )

        left_variance = self.variance(
            left
        )

        right_variance = self.variance(
            right
        )

        denominator = (
            left_variance
            * right_variance
        ) ** 0.5

        if denominator == 0 or covariance is None:
            return None

        return covariance / denominator

    def percentile(
        self,
        values: list[float],
        percentile: float,
    ) -> Optional[float]:
        if not values:
            return None

        ordered = sorted(
            values
        )

        index = min(
            len(ordered) - 1,
            max(
                0,
                round(
                    percentile
                    * (len(ordered) - 1)
                ),
            ),
        )

        return ordered[index]

    def entropy(
        self,
        values: list[float],
    ) -> Optional[float]:
        total = sum(
            value
            for value in values
            if value > 0
        )

        if total <= 0:
            return None

        result = 0.0

        for value in values:
            if value <= 0:
                continue

            probability = value / total
            result -= probability * log2(
                probability
            )

        return result

    def kl_divergence(
        self,
        observed: list[float],
        expected: list[float],
    ) -> Optional[float]:
        total_observed = sum(
            observed
        )
        total_expected = sum(
            expected
        )

        if (
            total_observed <= 0
            or total_expected <= 0
        ):
            return None

        result = 0.0

        for observed_value, expected_value in zip(
            observed,
            expected,
        ):
            if (
                observed_value <= 0
                or expected_value <= 0
            ):
                continue

            p = observed_value / total_observed
            q = expected_value / total_expected
            result += p * log2(
                p / q
            )

        return result


