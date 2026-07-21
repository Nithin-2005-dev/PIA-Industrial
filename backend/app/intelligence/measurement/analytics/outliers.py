from statistics import median


class OutlierDetectionEngine:

    def z_score_outliers(
        self,
        values: list[float],
        threshold: float = 3.0,
    ) -> list[int]:
        if len(
            values
        ) < 2:
            return []

        average = sum(values) / len(values)
        variance = sum(
            (
                value - average
            )
            ** 2
            for value in values
        ) / (
            len(values) - 1
        )
        deviation = variance ** 0.5

        if deviation == 0:
            return []

        return [
            index
            for index, value in enumerate(
                values
            )
            if abs(
                (
                    value - average
                )
                / deviation
            )
            > threshold
        ]

    def iqr_outliers(
        self,
        values: list[float],
        multiplier: float = 1.5,
    ) -> list[int]:
        if len(
            values
        ) < 4:
            return []

        ordered = sorted(
            values
        )
        midpoint = len(
            ordered
        ) // 2
        lower = ordered[:midpoint]
        upper = ordered[
            midpoint:
        ]
        q1 = median(
            lower
        )
        q3 = median(
            upper
        )
        iqr = q3 - q1
        low = q1 - multiplier * iqr
        high = q3 + multiplier * iqr

        return [
            index
            for index, value in enumerate(
                values
            )
            if value < low or value > high
        ]

    def mad_outliers(
        self,
        values: list[float],
        threshold: float = 3.5,
    ) -> list[int]:
        if len(
            values
        ) < 3:
            return []

        center = median(
            values
        )

        deviations = [
            abs(
                value - center
            )
            for value in values
        ]

        mad = median(
            deviations
        )

        if mad == 0:
            return []

        return [
            index
            for index, value in enumerate(
                values
            )
            if abs(
                0.6745
                * (
                    value - center
                )
                / mad
            )
            > threshold
        ]


