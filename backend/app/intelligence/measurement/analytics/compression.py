from dataclasses import dataclass
from random import Random


@dataclass(frozen=True)
class ApproximateHistogram:
    bins: tuple[float, ...]
    counts: tuple[int, ...]


class ReservoirSampler:

    def __init__(
        self,
        size: int,
        seed: int = 7,
    ):
        self._size = size
        self._random = Random(
            seed
        )
        self._count = 0
        self._sample = []

    def add(
        self,
        value,
    ):
        self._count += 1

        if len(
            self._sample
        ) < self._size:
            self._sample.append(
                value
            )
            return

        index = self._random.randint(
            1,
            self._count,
        )

        if index <= self._size:
            self._sample[
                index - 1
            ] = value

    def sample(
        self,
    ):
        return tuple(
            self._sample
        )


class ApproximateHistogramBuilder:

    def build(
        self,
        values: list[float],
        bucket_count: int = 10,
    ) -> ApproximateHistogram:
        if not values:
            return ApproximateHistogram(
                bins=(),
                counts=(),
            )

        minimum = min(
            values
        )
        maximum = max(
            values
        )

        if minimum == maximum:
            return ApproximateHistogram(
                bins=(minimum, maximum),
                counts=(len(values),),
            )

        width = (
            maximum - minimum
        ) / bucket_count
        counts = [
            0
            for _ in range(bucket_count)
        ]

        for value in values:
            index = min(
                bucket_count - 1,
                int(
                    (
                        value - minimum
                    )
                    / width
                ),
            )
            counts[
                index
            ] += 1

        bins = tuple(
            minimum + width * index
            for index in range(bucket_count + 1)
        )

        return ApproximateHistogram(
            bins=bins,
            counts=tuple(counts),
        )


