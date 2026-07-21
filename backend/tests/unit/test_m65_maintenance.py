"""Tests for M65 - Maintenance & Failure Intelligence."""
from __future__ import annotations

import datetime
from uuid import uuid4

from app.domain.entity_ref import EntityRef
from app.domain.industrial.asset import Asset
from app.intelligence.legacy.asset_intelligence_service import AssetIntelligenceService
from app.intelligence.legacy.maintenance_intelligence_service import MaintenanceIntelligenceService
from app.knowledge.graph.industrial_graph_manager import IndustrialGraphManager
from app.ingestion.observation.domain import (
    FailureEventFacts,
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


class TestMaintenanceIntelligenceService:
    def _create_obs(self, o_type, facts, timestamp, target_id):
        return Observation(
            observation_id=str(uuid4()),
            trace_id="t1",
            correlation_id="c1",
            timestamp=timestamp,
            observation_type=o_type,
            observation_category=ObservationCategory.OPERATIONS,
            source_platform="test",
            source_adapter="test",
            version="1.0",
            lifecycle=ObservationLifecycle.PRODUCTION,
            actors=(),
            targets=(EntityRef(id=target_id, type="asset"),),
            provenance=ObservationProvenance("test", "test", "doc"),
            context=ObservationContext(),
            facts=facts,
            processing_mode=ProcessingMode.LIVE,
        )

    def test_maintenance_intelligence(self):
        graph_manager = IndustrialGraphManager()
        obs_store = ObservationStore()
        
        # Setup Asset
        asset = Asset(id="P-101", name="Main Pump", equipment_tag="P-101", asset_type="Pump")
        graph_manager.builder.add_asset(asset)
        
        # Setup Timeline
        now = datetime.datetime.now(datetime.UTC)
        
        # 1. Inspection (Anomaly)
        obs_store.append(self._create_obs(
            ObservationType.INSPECTION_EVENT,
            InspectionFacts(inspection_id="i1", result="DETECTED", findings=("high vibration",)),
            now - datetime.timedelta(days=30),
            "P-101",
        ))
        
        # 2. Failure 1
        obs_store.append(self._create_obs(
            ObservationType.FAILURE,
            FailureEventFacts(failure_id="f1", failure_mode="vibration", description="bearing failure due to vibration"),
            now - datetime.timedelta(days=15),
            "P-101",
        ))
        
        # 3. Failure 2 (Repeated)
        obs_store.append(self._create_obs(
            ObservationType.FAILURE,
            FailureEventFacts(failure_id="f2", failure_mode="vibration", description="bearing failure again"),
            now - datetime.timedelta(days=2),
            "P-101",
        ))
        
        asset_service = AssetIntelligenceService(graph_manager, obs_store)
        maint_service = MaintenanceIntelligenceService(asset_service)
        
        # Test Precursors
        precursors = maint_service.detect_failure_precursors("P-101")
        assert len(precursors) == 2
        assert "vibration" in precursors[0].target_failure_mode.lower()
        
        # Test Repeated Failures
        patterns = maint_service.detect_repeated_failures("P-101")
        assert len(patterns) == 1
        assert patterns[0].occurrences == 2
        
        # Test Deferred Recommendations
        deferred = maint_service.detect_deferred_recommendations("P-101")
        assert len(deferred) == 1
        assert "Unresolved issue" in deferred[0].description
