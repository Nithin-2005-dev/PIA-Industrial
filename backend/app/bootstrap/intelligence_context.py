from app.estimator.expertise_projection import (
    ExpertiseProjection,
)

from app.query.expertise_query_service import (
    ExpertiseQueryService,
)

from app.intelligence.legacy.ownership_service import (
    OwnershipService,
)

from app.intelligence.legacy.policies.expertise_ownership_policy import (
    ExpertiseOwnershipPolicy,
)

from app.intelligence.legacy.successor_service import (
    SuccessorService,
)

from app.intelligence.legacy.policies.expertise_successor_policy import (
    ExpertiseSuccessorPolicy,
)

from app.coverage.coverage_service import (
    CoverageService,
)

from app.coverage.policies.expertise_coverage_policy import (
    ExpertiseCoveragePolicy,
)

from app.concentration.concentration_service import (
    ConcentrationService,
)

from app.concentration.policies.expertise_concentration_policy import (
    ExpertiseConcentrationPolicy,
)

from app.intelligence.risk.bus_factor_service import (
    BusFactorService,
)

from app.intelligence.risk.policies.ownership_bus_factor_policy import (
    OwnershipBusFactorPolicy,
)

from app.intelligence.assets.health_service import (
    HealthService,
)

from app.intelligence.assets.policies.organizational_health_policy import (
    OrganizationalHealthPolicy,
)

from app.history.health_projection import (
    HealthProjection,
)

from app.history.history_service import (
    HistoryService,
)

from app.intelligence.forecasting.forecast_service import (
    ForecastService,
)

from app.intelligence.forecasting.linear_forecast_policy import (
    LinearForecastPolicy,
)

from app.intelligence.forecasting.forecast_pipeline_service import (
    ForecastPipelineService,
)

from app.intelligence.forecasting.future_risk_pipeline_service import (
    FutureRiskPipelineService,
)

from app.intelligence.expertise.transfer_service import (
    TransferService,
)

from app.intelligence.expertise.policies.simple_transfer_policy import (
    SimpleTransferPolicy,
)



from app.intelligence.forecasting.forecast_severity_service import (
    ForecastSeverityService,
)

from app.intelligence.legacy.organization_risk_service import (
    OrganizationRiskService,
)

from app.intelligence.legacy.organization_health_service import (
    OrganizationHealthService,
)

from app.intelligence.legacy.organization_readiness_service import (
    OrganizationReadinessService,
)

from app.intelligence.legacy.organization_transfer_service import (
    OrganizationTransferService,
)

from app.intelligence.legacy.organization_dashboard_service import (
    OrganizationDashboardService,
)
from app.core.core_modules import (
    IntelligencePlatformModule,
    default_platform_modules,
)
from app.core.runtime import (
    PlatformRuntime,
)


class IntelligenceContext:

    def __init__(
        self,
        projection: ExpertiseProjection,
    ):

        self.projection = projection
        self.runtime = PlatformRuntime.create()
        for module in default_platform_modules():
            if module.name == "intelligence":
                continue
            self.runtime.register_module(module)
        self.runtime.register_module(
            IntelligencePlatformModule(
                projection=projection,
                context=self,
            )
        )
        self.platform = self.runtime.build()
        self.platform.initialize()
        provider = self.platform.provider

        self.query_service = provider.resolve(ExpertiseQueryService)
        self.ownership_service = provider.resolve(OwnershipService)
        self.successor_service = provider.resolve(SuccessorService)
        self.coverage_service = provider.resolve(CoverageService)
        self.concentration_service = provider.resolve(ConcentrationService)
        self.bus_factor_service = provider.resolve(BusFactorService)
        self.health_service = provider.resolve(HealthService)
        self.health_projection = provider.resolve(HealthProjection)
        self.history_service = provider.resolve(HistoryService)
        self.forecast_service = provider.resolve(ForecastService)
        self.forecast_pipeline_service = provider.resolve(ForecastPipelineService)
        self.future_risk_pipeline_service = provider.resolve(FutureRiskPipelineService)
        self.transfer_service = provider.resolve(TransferService)
        self.forecast_severity_service = provider.resolve(ForecastSeverityService)
        self.organization_risk_service = provider.resolve(OrganizationRiskService)
        self.organization_health_service = provider.resolve(OrganizationHealthService)
        self.organization_readiness_service = provider.resolve(OrganizationReadinessService)
        self.organization_transfer_service = provider.resolve(OrganizationTransferService)
        self.organization_dashboard_service = provider.resolve(OrganizationDashboardService)
