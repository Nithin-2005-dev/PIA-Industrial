from .organization_health import (
    OrganizationHealth,
)


class OrganizationHealthService:

    def __init__(
        self,
        intelligence_context,
    ):
        self._intelligence = (
            intelligence_context
        )

    def summary(
        self,
    ) -> OrganizationHealth:

        estimates = (
            self._intelligence
            .projection
            .all_estimates()
        )

        coverage_reports = (
            self._intelligence
            .coverage_service
            .analyze(
                estimates
            )
        )

        concentration_reports = (
            self._intelligence
            .concentration_service
            .analyze(
                estimates
            )
        )

        bus_factors = []

        module_ids = {
            estimate.module_ref.id
            for estimate in estimates
        }

        for module_id in module_ids:

            bus_factors.append(
                self._intelligence
                .bus_factor_service
                .analyze(
                    module_id
                )
            )

        health_reports = (
            self._intelligence
            .health_service
            .analyze(
                coverage_reports,
                concentration_reports,
                bus_factors,
            )
        )

        if not health_reports:

            return OrganizationHealth(
                average_health=0.0,
                best_health=0.0,
                worst_health=0.0,
                healthy_modules=0,
                warning_modules=0,
                critical_modules=0,
                total_modules=0,
            )

        total = sum(
            report.health_score
            for report in health_reports
        )

        healthy = sum(
            1
            for report in health_reports
            if report.health_level
            == "HEALTHY"
        )

        warning = sum(
            1
            for report in health_reports
            if report.health_level
            == "WARNING"
        )

        critical = sum(
            1
            for report in health_reports
            if report.health_level
            == "CRITICAL"
        )

        best_health = max(
            report.health_score
            for report in health_reports
        )

        worst_health = min(
            report.health_score
            for report in health_reports
        )

        return OrganizationHealth(
            average_health=(
                total
                / len(health_reports)
            ),
            best_health=best_health,
            worst_health=worst_health,
            healthy_modules=healthy,
            warning_modules=warning,
            critical_modules=critical,
            total_modules=len(
                health_reports
            ),
        )