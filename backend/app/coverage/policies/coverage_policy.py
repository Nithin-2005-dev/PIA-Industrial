from abc import ABC, abstractmethod

from app.coverage.coverage_report import (
    CoverageReport,
)


class CoveragePolicy(
    ABC
):

    @abstractmethod
    def analyze(
        self,
        expertise_estimates,
    ) -> list[CoverageReport]:
        pass