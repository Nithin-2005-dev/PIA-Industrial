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
    def _create_obs(self, facts, timestamp):
        return Observation(
            observation_id=str(uuid4()),
            trace_id="t1",
            correlation_id="c1",
            timestamp=timestamp,
            observation_type=ObservationType.INSPECTION_EVENT,
            observation_category=ObservationCategory.INSPECTION,
            source_platform="test",
            source_adapter="test",
            version="1.0",
            lifecycle=ObservationLifecycle.PRODUCTION,
            actors=(),
            targets=(EntityRef(id="P-101", type="asset"),),
            provenance=ObservationProvenance("test", "test", "doc123"),
            context=ObservationContext(),
            facts=facts,
            processing_mode=ProcessingMode.LIVE,
        )

    def test_generate_portfolio(self):
        graph_manager = IndustrialGraphManager()
        obs_store = ObservationStore()
        asset = Asset(id="P-101", name="Main Pump", equipment_tag="P-101", asset_type="Pump")
        graph_manager.builder.add_asset(asset)
        
        # Missing evidence causes a compliance gap
        
        # Only one inspector causes an expertise risk
        now = datetime.datetime.now(datetime.UTC)
        old_date = now - datetime.timedelta(days=400)
        obs_store.append(self._create_obs(
            InspectionFacts(inspection_id="i1", result="SATISFACTORY", inspector="Alice"),
            old_date,
        ))
        
        asset_service = AssetIntelligenceService(graph_manager, obs_store)
        maint_service = MaintenanceIntelligenceService(asset_service)
        rca_service = IndustrialCausalRCA(asset_service, maint_service)
        comp_service = ComplianceIntelligenceService(asset_service)
        exp_service = ExpertiseIntelligenceService(asset_service)
        
        dec_service = DecisionIntelligenceService(
            asset_service, maint_service, rca_service, comp_service, exp_service
        )
        
        portfolio = dec_service.generate_portfolio(["P-101"])
        
        # Should have a compliance intervention and a training intervention
        assert len(portfolio.interventions) >= 1
        
        # Check prioritization (compliance first)
        assert portfolio.interventions[0].compliance_impact is True
        
        # Ensure training is there
        training = [i for i in portfolio.interventions if i.action_type == "TRAINING"]
        assert len(training) == 1
