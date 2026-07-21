from .organization_risk import (
    OrganizationRisk,
)


class OrganizationRiskService:

    def __init__(
        self,
        intelligence_context,
    ):
        self._intelligence = (
            intelligence_context
        )

    def top_risks(
        self,
        horizon: int = 3,
        limit: int = 10,
    ):

        future_risks = (
            self._intelligence
            .future_risk_pipeline_service
            .ranking(
                horizon=horizon,
                limit=limit,
            )
        )

        severities = {
            severity.module_ref.id: severity
            for severity in (
                self._intelligence
                .future_risk_pipeline_service
                .severities(
                    horizon
                )
            )
        }

        rankings = []

        for index, risk in enumerate(
            future_risks,
            start=1,
        ):

            severity = (
                severities[
                    risk.module_ref.id
                ]
            )

            rankings.append(
                OrganizationRisk(
                    module_ref=(
                        risk.module_ref
                    ),
                    health_score=(
                        risk.current_health
                    ),
                    future_risk_score=(
                        risk.risk_score
                    ),
                    severity_level=(
                        severity
                        .severity_level
                    ),
                    rank=index,
                )
            )

        return rankings