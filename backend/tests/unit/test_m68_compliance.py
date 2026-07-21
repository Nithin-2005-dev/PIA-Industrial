"""Tests for M68 - Compliance Intelligence."""
from __future__ import annotations

import datetime
from uuid import uuid4

from app.domain.entity_ref import EntityRef
from app.domain.industrial.asset import Asset
from app.intelligence.legacy.asset_intelligence_service import AssetIntelligenceService
from app.intelligence.legacy.compliance_intelligence_service import ComplianceIntelligenceService
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


class TestComplianceIntelligenceService:
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

    def test_evaluate_compliance_overdue(self):
        graph_manager = IndustrialGraphManager()
        obs_store = ObservationStore()
        
        asset = Asset(id="P-101", name="Main Pump", equipment_tag="P-101", asset_type="Pump")
        graph_manager.builder.add_asset(asset)
        
        # 400 days ago, requirement is 365 days
        now = datetime.datetime.now(datetime.UTC)
        old_date = now - datetime.timedelta(days=400)
        
        obs_store.append(self._create_obs(
            InspectionFacts(inspection_id="i1", result="SATISFACTORY"),
            old_date,
        ))
        
        asset_service = AssetIntelligenceService(graph_manager, obs_store)
        comp_service = ComplianceIntelligenceService(asset_service)
        
        pkg = comp_service.evaluate_compliance("P-101")
        
        assert pkg.compliant is False
        assert len(pkg.gaps) == 1
        assert pkg.gaps[0].status == "OVERDUE"
        assert pkg.gaps[0].days_overdue == 400 - 365
        assert "doc123" in pkg.supporting_documents

    def test_evaluate_compliance_missing(self):
        graph_manager = IndustrialGraphManager()
        obs_store = ObservationStore()
        asset = Asset(id="P-101", name="Main Pump", equipment_tag="P-101", asset_type="Pump")
        graph_manager.builder.add_asset(asset)
        
        asset_service = AssetIntelligenceService(graph_manager, obs_store)
        comp_service = ComplianceIntelligenceService(asset_service)
        
        pkg = comp_service.evaluate_compliance("P-101")
        
        assert pkg.compliant is True
        assert len(pkg.gaps) == 0
