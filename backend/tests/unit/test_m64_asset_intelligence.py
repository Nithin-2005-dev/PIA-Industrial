"""Tests for M64 - Asset Intelligence."""
from __future__ import annotations

import datetime
from uuid import uuid4

from app.domain.entity_ref import EntityRef
from app.domain.industrial.asset import Asset
from app.intelligence.legacy.asset_intelligence_service import AssetIntelligenceService
from app.knowledge.graph.industrial_graph_manager import IndustrialGraphManager
from app.ingestion.observation.domain import (
    FailureEventFacts,
    Observation,
    ObservationCategory,
    ObservationContext,
    ObservationLifecycle,
    ObservationProvenance,
    ObservationType,
    ProcessingMode,
)
from app.ingestion.observation.storage import ObservationStore


class TestAssetIntelligenceService:
    def test_get_asset_profile_and_timeline(self):
        graph_manager = IndustrialGraphManager()
        obs_store = ObservationStore()
        
        # 1. Setup Graph with Asset
        asset = Asset(id="P-101", name="Main Pump", equipment_tag="P-101", asset_type="Pump")
        graph_manager.builder.add_asset(asset)
        
        # 2. Add Observation targeting Asset directly
        obs = Observation(
            observation_id=str(uuid4()),
            trace_id="t1",
            correlation_id="c1",
            timestamp=datetime.datetime.now(datetime.UTC),
            observation_type=ObservationType.FAILURE,
            observation_category=ObservationCategory.RELIABILITY,
            source_platform="test",
            source_adapter="test",
            version="1.0",
            lifecycle=ObservationLifecycle.PRODUCTION,
            actors=(),
            targets=(EntityRef(id="P-101", type="asset"),),
            provenance=ObservationProvenance("test", "test", "doc1"),
            context=ObservationContext(),
            facts=FailureEventFacts(
                failure_id="f1",
                failure_mode="bearing_seizure",
                description="Seized bearing",
            ),
            processing_mode=ProcessingMode.LIVE,
        )
        obs_store.append(obs)
        
        # 3. Test Service
        service = AssetIntelligenceService(graph_manager, obs_store)
        profile = service.get_asset_profile("P-101")
        
        assert profile is not None
        assert profile.asset_id == "P-101"
        assert profile.name == "Main Pump"
        
        # Timeline should contain the failure observation
        assert len(profile.timeline) == 1
        assert profile.timeline[0].event_type == ObservationType.FAILURE.value
        assert profile.timeline[0].description == "Seized bearing"
