"""Tests for M70 - Decision Intelligence."""
from __future__ import annotations

import datetime
from uuid import uuid4

from app.domain.entity_ref import EntityRef
from app.domain.industrial.asset import Asset
from app.intelligence.legacy.asset_intelligence_service import AssetIntelligenceService
from app.intelligence.legacy.compliance_intelligence_service import ComplianceIntelligenceService
from app.intelligence.legacy.decision_intelligence_service import DecisionIntelligenceService
from app.intelligence.legacy.expertise_intelligence_service import ExpertiseIntelligenceService
from app.intelligence.legacy.industrial_causal_rca import IndustrialCausalRCA
from app.intelligence.legacy.maintenance_intelligence_service import MaintenanceIntelligenceService
from app.knowledge.graph.industrial_graph_manager import IndustrialGraphManager
from app.ingestion.observation.domain import (
    InspectionFacts,
    Observation,
    ObservationCategory,
    ObservationContext,
    ObservationLifecycle,
    ObservationProvenance,
    ObservationType,
    ProcessingMode,
)
from app.ingestion.observation.storage import ObservationStore


class TestDecisionIntelligenceService:
    def test_generate_portfolio(self):
        graph_manager = IndustrialGraphManager()
        obs_store = ObservationStore()
        asset = Asset(id="P-101", name="Main Pump", equipment_tag="P-101", asset_type="Pump")
        graph_manager.builder.add_asset(asset)
        
        asset_service = AssetIntelligenceService(graph_manager, obs_store)
        maint_service = MaintenanceIntelligenceService(asset_service)
        rca_engine = IndustrialCausalRCA(asset_service, maint_service)
        comp_service = ComplianceIntelligenceService(asset_service)
        exp_service = ExpertiseIntelligenceService(asset_service)
        
        dec_service = DecisionIntelligenceService(
            asset_service, maint_service, rca_engine, comp_service, exp_service
        )
        
        portfolio = dec_service.generate_portfolio(["P-101"])
        
        assert portfolio.portfolio_id is not None
        assert portfolio.total_estimated_cost == 0.0
        assert portfolio.overall_risk_reduction == 0.0
