from app.intelligence.counterfactual.simulation_result import (
    SimulationResult,
)

from app.intelligence.counterfactual.simulation_service import (
    SimulationService,
)


class DepartureScenarioService:

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
    ) -> SimulationResult:

        module_id = (
            request.module_id
        )

        developer_id = (
            request.departing_owner_id
        )

        owners = (
            self._intelligence
            .ownership_service
            .owners_of(
                module_id
            )
        )

        ownership = next(
            (
                owner
                for owner in owners
                if (
                    owner.owner_ref.id
                    ==
                    developer_id
                )
            ),
            None,
        )

        if ownership is None:

            raise ValueError(
                f"No ownership found "
                f"for {developer_id}"
            )

        successors = (
            self._intelligence
            .successor_service
            .recommend(
                module_id,
                limit=1,
            )
        )

        if not successors:

            raise ValueError(
                f"No successor found "
                f"for {module_id}"
            )

        successor_name = (
            successors[0]
            .developer_ref
            .id
        )

        readiness = (
            self._intelligence
            .readiness_service
            .readiness_of(
                successor_name,
                module_id,
            )
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

        return (
            SimulationService()
            .simulate_departure(
                health_report=(
                    health_report
                ),
                ownership_estimate=(
                    ownership
                ),
                readiness_score=(
                    readiness
                    .readiness_score
                ),
            )
        )