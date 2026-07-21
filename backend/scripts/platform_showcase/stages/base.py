"""
===============================================================================

Platform Showcase Base Stage

===============================================================================

Every showcase stage inherits from PipelineStage.

Responsibilities

✓ Timing
✓ Console rendering
✓ Statistics helpers
✓ Safe execution
✓ Common analytics

Business logic belongs only inside the derived stage.

===============================================================================
"""

from __future__ import annotations

import time
from abc import ABC
from collections import Counter
from statistics import mean

from ..context import PlatformContext

from ..ui import (
    section,
    metric,
    success,
    warning,
)


class PipelineStage(ABC):

    name = "Unnamed Stage"

    # ---------------------------------------------------------------------

    def execute(
        self,
        context: PlatformContext,
    ) -> None:
        raise NotImplementedError

    # ---------------------------------------------------------------------

    def run(
        self,
        context: PlatformContext,
    ) -> None:

        started = time.perf_counter()

        section(self.name)

        self.execute(context)

        elapsed = time.perf_counter() - started

        success(
            f"{self.name} completed in {elapsed:.3f}s"
        )

        context.stage(self.name).duration = elapsed

    # ---------------------------------------------------------------------
    # Generic helpers
    # ---------------------------------------------------------------------

    def counter(
        self,
        iterable,
    ) -> Counter:

        return Counter(iterable)

    # ---------------------------------------------------------------------

    def average(
        self,
        values,
    ) -> float:

        values = list(values)

        if not values:
            return 0.0

        return mean(values)

    # ---------------------------------------------------------------------

    def percentage(
        self,
        numerator: int,
        denominator: int,
    ) -> float:

        if denominator == 0:
            return 0.0

        return (numerator / denominator) * 100.0

    # ---------------------------------------------------------------------

    def print_counter(
        self,
        title: str,
        counter: Counter,
        limit: int = 10,
    ):

        section(title)

        if not counter:

            warning("No data")

            return

        for key, value in counter.most_common(limit):

            metric(str(key), value)

    # ---------------------------------------------------------------------

    def divider(
        self,
    ):

        print("-" * 80)

    # ---------------------------------------------------------------------

    def headline(
        self,
        text: str,
    ):

        print()
        print("=" * 80)
        print(text.center(80))
        print("=" * 80)
