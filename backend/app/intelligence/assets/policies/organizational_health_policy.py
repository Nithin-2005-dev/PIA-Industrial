from app.intelligence.assets.health_report import (
    HealthReport,
)

from .health_policy import (
    HealthPolicy,
)


class OrganizationalHealthPolicy(
    HealthPolicy
):

    THRESHOLD_HEALTHY = 75.0
    THRESHOLD_WARNING = 50.0
    POWER_MEAN_P = 0.3

    def _bus_factor_health(
        self,
        bus_factor: int,
    ) -> float:

        if bus_factor >= 4:
            return 100.0

        if bus_factor == 3:
            return 75.0

        if bus_factor == 2:
            return 50.0

        return 25.0

    def evaluate(
        self,
        coverage_reports,
        concentration_reports,
        bus_factor_reports,
    ):

        concentration_by_module = {
            report.module_ref.id: report
            for report in concentration_reports
        }

        bus_factor_by_module = {
            report.module_ref.id: report
            for report in bus_factor_reports
        }

        reports = []

        for coverage in coverage_reports:

            module_id = (
                coverage.module_ref.id
            )

            concentration = (
                concentration_by_module[
                    module_id
                ]
            )

            bus_factor = (
                bus_factor_by_module[
                    module_id
                ]
            )

            concentration_health = (
                1
                - concentration
                .concentration_score
            ) * 100

            bus_health = (
                self._bus_factor_health(
                    bus_factor.value
                )
            )

            # Ensure values are strictly positive for power mean
            v1 = max(0.01, coverage.coverage_score / 100.0)
            v2 = max(0.01, concentration_health / 100.0)
            v3 = max(0.01, bus_health / 100.0)

            # Fetch uncertainty/confidence or use defaults
            u1 = getattr(coverage, "coverage_uncertainty", 0.1)
            u2 = getattr(concentration, "concentration_uncertainty", 0.1)
            u3 = getattr(bus_factor, "uncertainty", 0.1)

            c1 = getattr(coverage, "coverage_confidence", 0.9)
            c2 = getattr(concentration, "concentration_confidence", 0.9)
            c3 = getattr(bus_factor, "confidence", 0.9)

            # Weight by base importance and metric confidence
            w1 = 0.4 * c1
            w2 = 0.4 * c2
            w3 = 0.2 * c3
            total_w = w1 + w2 + w3

            # Confidence-Weighted Power Mean (p=0.3)
            p = self.POWER_MEAN_P
            power_sum = w1 * (v1**p) + w2 * (v2**p) + w3 * (v3**p)
            health_score_0_1 = (power_sum / total_w) ** (1/p)
            health_score = health_score_0_1 * 100.0

            # Propagate uncertainty linearly (weighted)
            health_uncertainty = (w1 * u1 + w2 * u2 + w3 * u3) / total_w
            health_confidence = 1.0 - health_uncertainty

            if health_score >= self.THRESHOLD_HEALTHY:

                level = "HEALTHY"

            elif health_score >= self.THRESHOLD_WARNING:

                level = "WARNING"

            else:

                level = "CRITICAL"

            reports.append(
                HealthReport(
                    module_ref=(
                        coverage.module_ref
                    ),
                    health_score=(
                        health_score
                    ),
                    health_uncertainty=health_uncertainty,
                    health_confidence=health_confidence,
                    health_level=(
                        level
                    ),
                    coverage_score=(
                        coverage.coverage_score
                    ),
                    concentration_score=(
                        concentration
                        .concentration_score
                    ),
                    bus_factor=(
                        bus_factor
                        .value
                    ),
                )
            )

        reports.sort(
            key=lambda report: (
                report.health_score
            ),
            reverse=True,
        )

        return reports