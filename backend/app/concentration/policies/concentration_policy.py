from abc import ABC, abstractmethod

from app.concentration.concentration_report import (
    ConcentrationReport,
)


class ConcentrationPolicy(
    ABC
):

    @abstractmethod
    def analyze(
        self,
        expertise_estimates,
    ) -> list[ConcentrationReport]:
        pass