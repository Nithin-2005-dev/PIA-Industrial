from abc import ABC, abstractmethod

from app.intelligence.assets.health_report import (
    HealthReport,
)


class HealthPolicy(
    ABC
):

    @abstractmethod
    def evaluate(
        self,
        coverage_reports,
        concentration_reports,
        bus_factor_reports,
    ) -> list[HealthReport]:
        pass