from dataclasses import dataclass

from .coverage_report import (
    CoverageReport,
)


@dataclass(frozen=True)
class CoverageGap:
    """
    Ranked coverage issue.
    """

    report: CoverageReport

    rank: int