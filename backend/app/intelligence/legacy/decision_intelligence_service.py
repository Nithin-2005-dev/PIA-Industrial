"""Decision Intelligence Service.

Generates and prioritizes a portfolio of interventions based on asset intelligence,
causal RCA, simulation, and compliance data.
"""
from __future__ import annotations

import logging
from uuid import uuid4

from app.domain.industrial.decision_intelligence import (
    IndustrialInterventionPortfolio,
    ProposedIntervention,
)
from app.intelligence.legacy.asset_intelligence_service import AssetIntelligenceService
from app.intelligence.legacy.compliance_intelligence_service import ComplianceIntelligenceService
from app.intelligence.legacy.expertise_intelligence_service import ExpertiseIntelligenceService
from app.intelligence.legacy.industrial_causal_rca import IndustrialCausalRCA
from app.intelligence.legacy.maintenance_intelligence_service import MaintenanceIntelligenceService

logger = logging.getLogger(__name__)


class DecisionIntelligenceService:
    """Service to generate deterministic prioritized interventions."""

    def __init__(
        self,
        asset_service: AssetIntelligenceService,
        maintenance_service: MaintenanceIntelligenceService,
        rca_service: IndustrialCausalRCA,
        compliance_service: ComplianceIntelligenceService,
        expertise_service: ExpertiseIntelligenceService,
    ):
        self._asset_service = asset_service
        self._maintenance_service = maintenance_service
        self._rca_service = rca_service
        self._compliance_service = compliance_service
        self._expertise_service = expertise_service

    def generate_portfolio(self, asset_ids: list[str]) -> IndustrialInterventionPortfolio:
        """Evaluate assets and generate a prioritized portfolio."""
        interventions: list[ProposedIntervention] = []
        
        for asset_id in asset_ids:
            profile = self._asset_service.get_asset_profile(asset_id)
            if not profile:
                continue
                
            # 1. Compliance
            comp_pkg = self._compliance_service.evaluate_compliance(asset_id)
            if not comp_pkg.compliant:
                for gap in comp_pkg.gaps:
                    interventions.append(
                        ProposedIntervention(
                            intervention_id=str(uuid4()),
                            asset_id=asset_id,
                            action_type="INSPECTION",
                            title=f"Resolve Compliance Gap: {gap.requirement_id}",
                            description=f"Required inspection is {gap.status}.",
                            estimated_cost=5000.0,
                            risk_reduction_score=0.2,
                            compliance_impact=True,
                        )
                    )
            
            # 2. Maintenance & RCA
            # For simplicity, we just use MaintenanceIntelligence to suggest maintenance
            maint_intel = self._maintenance_service.analyze_asset(asset_id)
            if maint_intel.get("deferred_recommendations") or maint_intel.get("repeated_failures"):
                interventions.append(
                    ProposedIntervention(
                        intervention_id=str(uuid4()),
                        asset_id=asset_id,
                        action_type="MAINTENANCE",
                        title=f"Perform Critical Maintenance on {asset_id}",
                        description="Address deferred recommendations and repeated failures.",
                        estimated_cost=25000.0,
                        risk_reduction_score=0.5,
                        compliance_impact=False,
                    )
                )
                
            # 3. Expertise - Removed legacy software-engineering bus-factor logic
            # Industrial expertise requires actual personnel/skill evidence.

        # Sort by compliance impact (True first), then risk reduction score (descending)
        interventions.sort(key=lambda i: (not i.compliance_impact, -i.risk_reduction_score))
        
        total_cost = sum(i.estimated_cost for i in interventions)
        total_risk = sum(i.risk_reduction_score for i in interventions)
        
        return IndustrialInterventionPortfolio(
            portfolio_id=str(uuid4()),
            interventions=tuple(interventions),
            total_estimated_cost=total_cost,
            overall_risk_reduction=total_risk,
        )
