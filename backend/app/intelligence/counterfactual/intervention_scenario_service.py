from app.intelligence.counterfactual.intervention_impact_service import (
    InterventionImpactService,
)

from .scenario_execution_service import (
    ScenarioExecutionService,
)


class InterventionScenarioService:

    def __init__(
        self,
        intelligence_context,
    ):

        self._intelligence = (
            intelligence_context
        )

    def evaluate(
        self,
        request,
    ):

        module_id = (
            request.module_id
        )

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

        bus_factor = (
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
                [bus_factor],
            )
        )

        health_report = next(
            (
                report
                for report
                in health_reports
                if (
                    report.module_ref.id
                    ==
                    module_id
                )
            ),
            None,
        )

        if health_report is None:

            raise ValueError(
                f"No health report "
                f"for {module_id}"
            )

        severity_reports = (
            self._intelligence
            .future_risk_pipeline_service
            .severities(
                request.horizon
            )
        )

        severity_report = next(
            (
                report
                for report
                in severity_reports
                if (
                    report.module_ref.id
                    ==
                    module_id
                )
            ),
            None,
        )

        if severity_report is None:

            raise ValueError(
                f"No severity report "
                f"for {module_id}"
            )

        coverage_report = next(
            (
                report
                for report
                in coverage_reports
                if (
                    report.module_ref.id
                    ==
                    module_id
                )
            ),
            None,
        )

        concentration_report = next(
            (
                report
                for report
                in concentration_reports
                if (
                    report.module_ref.id
                    ==
                    module_id
                )
            ),
            None,
        )

        impacts = (
            InterventionImpactService()
            .estimate(
                coverage_report=(
                    coverage_report
                ),
                concentration_report=(
                    concentration_report
                ),
                severity_report=(
                    severity_report
                ),
            )
        )

        outcomes = []

        baseline_health = (
            health_report
            .health_score
        )

        baseline_risk = (
            severity_report
            .severity_score
            * 100
        )

        outcomes.append(
            ScenarioExecutionService()
            .execute(
                request=request,
                predicted_health=(
                    baseline_health
                ),
                future_risk_score=(
                    baseline_risk
                ),
            )
        )

        for impact in impacts:

            outcomes.append(
                ScenarioExecutionService()
                .execute(
                    request=type(
                        "Strategy",
                        (),
                        {
                            "strategy_name":
                            impact.action
                        },
                    )(),
                    predicted_health=(
                        baseline_health
                        +
                        impact
                        .expected_health_gain
                    ),
                    future_risk_score=max(
                        0,
                        baseline_risk
                        -
                        impact
                        .expected_health_gain,
                    ),
                )
            )

        return outcomes