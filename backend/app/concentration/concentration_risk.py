from dataclasses import dataclass

from .concentration_report import (
    ConcentrationReport,
)


@dataclass(frozen=True)
class ConcentrationRisk:
    """
    Ranked concentration risk.
    """

    report: ConcentrationReport

    rank: int