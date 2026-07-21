from .organization_dashboard import (
    OrganizationDashboard,
)


class OrganizationDashboardService:

    def __init__(
        self,
        intelligence_context,
    ):
        self._intelligence = (
            intelligence_context
        )

    def dashboard(
        self,
        risk_limit: int = 10,
        readiness_limit: int = 10,
        transfer_limit: int = 10,
        horizon: int = 3,
    ):

        health = (
            self._intelligence
            .organization_health_service
            .summary()
        )

        risks = (
            self._intelligence
            .organization_risk_service
            .top_risks(
                horizon=horizon,
                limit=risk_limit,
            )
        )

        readiness = (
            self._intelligence
            .organization_readiness_service
            .weakest_modules(
                limit=readiness_limit,
            )
        )

        transfers = (
            self._intelligence
            .organization_transfer_service
            .top_opportunities(
                limit=transfer_limit,
            )
        )

        return OrganizationDashboard(
            health=health,
            risks=risks,
            readiness=readiness,
            transfers=transfers,
        )