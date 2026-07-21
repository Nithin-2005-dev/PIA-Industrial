from __future__ import annotations

from math import log2
from math import sqrt


class ScientificStatistics:
    def mean(self, values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    def variance(self, values: list[float]) -> float:
        if len(values) < 2:
            return 0.0
        avg = self.mean(values)
        return sum((value - avg) ** 2 for value in values) / (len(values) - 1)

    def standard_deviation(self, values: list[float]) -> float:
        return sqrt(self.variance(values))

    def entropy(self, values: list[float]) -> float:
        total = sum(value for value in values if value > 0)
        if total <= 0:
            return 0.0
        result = 0.0
        for value in values:
            if value <= 0:
                continue
            probability = value / total
            result -= probability * log2(probability)
        return result

    def quantile(self, values: list[float], q: float) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        index = round(max(0.0, min(1.0, q)) * (len(ordered) - 1))
        return float(ordered[index])

    def histogram(self, values: list[float], bins: int) -> dict[str, int]:
        if bins <= 0:
            raise ValueError("bins must be positive")
        if not values:
            return {}
        low = min(values)
        high = max(values)
        if low == high:
            return {f"{low}:{high}": len(values)}
        width = (high - low) / bins
        counts = {f"{low + i * width}:{low + (i + 1) * width}": 0 for i in range(bins)}
        keys = list(counts.keys())
        for value in values:
            index = min(bins - 1, int((value - low) / width))
            counts[keys[index]] += 1
        return counts

    def correlation(self, left: list[float], right: list[float]) -> float:
        count = min(len(left), len(right))
        if count < 2:
            return 0.0
        left = left[:count]
        right = right[:count]
        left_avg = self.mean(left)
        right_avg = self.mean(right)
        numerator = sum((left[i] - left_avg) * (right[i] - right_avg) for i in range(count))
        left_den = sum((value - left_avg) ** 2 for value in left)
        right_den = sum((value - right_avg) ** 2 for value in right)
        denominator = sqrt(left_den * right_den)
        return numerator / denominator if denominator else 0.0

    def distribution_analysis(self, values: list[float]) -> dict[str, float]:
        return {
            "mean": self.mean(values),
            "variance": self.variance(values),
            "standard_deviation": self.standard_deviation(values),
            "p50": self.quantile(values, 0.5),
            "p95": self.quantile(values, 0.95),
            "entropy": self.entropy(values),
        }

