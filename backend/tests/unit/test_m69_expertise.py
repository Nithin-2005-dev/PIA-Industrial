"""Tests for M69 - Expertise Intelligence."""
from __future__ import annotations

import datetime
from uuid import uuid4

from app.domain.entity_ref import EntityRef
from app.domain.industrial.asset import Asset
from app.intelligence.legacy.asset_intelligence_service import AssetIntelligenceService
from app.intelligence.legacy.expertise_intelligence_service import ExpertiseIntelligenceService
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


class TestExpertiseIntelligenceService:
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

    def test_evaluate_expertise(self):
        graph_manager = IndustrialGraphManager()
        obs_store = ObservationStore()
        
        asset = Asset(id="P-101", name="Main Pump", equipment_tag="P-101", asset_type="Pump")
        graph_manager.builder.add_asset(asset)
        
        now = datetime.datetime.now(datetime.UTC)
        
        # 3 inspections by Alice, 1 by Bob
        obs_store.append(self._create_obs(
            InspectionFacts(inspection_id="i1", result="SATISFACTORY", inspector="Alice"),
            now,
        ))
        obs_store.append(self._create_obs(
            InspectionFacts(inspection_id="i2", result="SATISFACTORY", inspector="Alice"),
            now,
        ))
        obs_store.append(self._create_obs(
            InspectionFacts(inspection_id="i3", result="SATISFACTORY", inspector="Alice"),
            now,
        ))
        obs_store.append(self._create_obs(
            InspectionFacts(inspection_id="i4", result="SATISFACTORY", inspector="Bob"),
            now,
        ))
        
        asset_service = AssetIntelligenceService(graph_manager, obs_store)
        exp_service = ExpertiseIntelligenceService(asset_service)
        
        concentration = exp_service.evaluate_expertise("P-101")
        
        assert concentration.expert_count == 2
        assert concentration.top_expert_id == "Alice"
        assert concentration.concentration_score == 0.75  # 3/4
        assert concentration.risk_level == "MEDIUM"

    def test_evaluate_expertise_single_point(self):
        graph_manager = IndustrialGraphManager()
        obs_store = ObservationStore()
        asset = Asset(id="P-101", name="Main Pump", equipment_tag="P-101", asset_type="Pump")
        graph_manager.builder.add_asset(asset)
        
        now = datetime.datetime.now(datetime.UTC)
        obs_store.append(self._create_obs(
            InspectionFacts(inspection_id="i1", result="SATISFACTORY", inspector="Alice"),
            now,
        ))
        
        asset_service = AssetIntelligenceService(graph_manager, obs_store)
        exp_service = ExpertiseIntelligenceService(asset_service)
        
        concentration = exp_service.evaluate_expertise("P-101")
        
        assert concentration.expert_count == 1
        assert concentration.top_expert_id == "Alice"
        assert concentration.concentration_score == 1.0
        assert concentration.risk_level == "HIGH"
