"""Global singletons for the Industrial Demo.

Preloads the deterministic state required for the Pump P-101 Hackathon Demo.
"""
from __future__ import annotations

import datetime

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

# Global Instances
_graph_manager: IndustrialGraphManager | None = None
_obs_store: ObservationStore | None = None


def init_demo_state() -> None:
    """Initialize the global state with the P-101 scenario."""
    global _graph_manager, _obs_store
    
    if _graph_manager is not None:
        return
        
    _graph_manager = IndustrialGraphManager()
    _obs_store = ObservationStore()
    
    # 1. Add Asset P-101
    asset = Asset(id="P-101", name="Main Centrifugal Pump", equipment_tag="P-101", asset_type="Pump")
    _graph_manager.builder.add_asset(asset)
    
    # 2. Add some secondary assets
    asset2 = Asset(id="P-102", name="Auxiliary Centrifugal Pump", equipment_tag="P-102", asset_type="Pump")
    _graph_manager.builder.add_asset(asset2)
    
    asset3 = Asset(id="V-204", name="Cooling Vessel", equipment_tag="V-204", asset_type="Vessel")
    _graph_manager.builder.add_asset(asset3)
    
    now = datetime.datetime.now(datetime.UTC)
    
    # 3. Add an old inspection to trigger a compliance gap for P-101
    old_date = now - datetime.timedelta(days=400)
    _obs_store.append(
        Observation(
            observation_id="obs_1",
            trace_id="t1",
            correlation_id="c1",
            timestamp=old_date,
            observation_type=ObservationType.INSPECTION_EVENT,
            observation_category=ObservationCategory.INSPECTION,
            source_platform="Maximo",
            source_adapter="industrial",
            version="1.0",
            lifecycle=ObservationLifecycle.PRODUCTION,
            actors=(),
            targets=(EntityRef(id="P-101", type="asset"),),
            provenance=ObservationProvenance("Maximo", "industrial", "doc_insp_1"),
            context=ObservationContext(),
            facts=InspectionFacts(
                inspection_id="insp_1", 
                result="SATISFACTORY", 
                inspector="Alice",
            ),
            processing_mode=ProcessingMode.LIVE,
        )
    )
    
    # 4. Add a precursor inspection (high vibration)
    _obs_store.append(
        Observation(
            observation_id="obs_precursor",
            trace_id="t1",
            correlation_id="c1_2",
            timestamp=now - datetime.timedelta(days=20),
            observation_type=ObservationType.INSPECTION_EVENT,
            observation_category=ObservationCategory.INSPECTION,
            source_platform="Maximo",
            source_adapter="industrial",
            version="1.0",
            lifecycle=ObservationLifecycle.PRODUCTION,
            actors=(),
            targets=(EntityRef(id="P-101", type="asset"),),
            provenance=ObservationProvenance("Maximo", "industrial", "doc_insp_2"),
            context=ObservationContext(),
            facts=InspectionFacts(
                inspection_id="insp_2", 
                result="DETECTED",
                findings=("high vibration",),
                inspector="Alice",
            ),
            processing_mode=ProcessingMode.LIVE,
        )
    )
    
    # 5. Add a failure event with precursors
    _obs_store.append(
        Observation(
            observation_id="obs_2",
            trace_id="t1",
            correlation_id="c2",
            timestamp=now - datetime.timedelta(days=10),
            observation_type=ObservationType.FAILURE,
            observation_category=ObservationCategory.INSPECTION,
            source_platform="Maximo",
            source_adapter="industrial",
            version="1.0",
            lifecycle=ObservationLifecycle.PRODUCTION,
            actors=(),
            targets=(EntityRef(id="P-101", type="asset"),),
            provenance=ObservationProvenance("Maximo", "industrial", "doc_fail_1"),
            context=ObservationContext(),
            facts=InspectionFacts(
                inspection_id="fail_1", 
                result="FAILED", 
                findings=("high vibration leading to bearing failure",),
                inspector="Bob",
            ),
            processing_mode=ProcessingMode.LIVE,
        )
    )
    
    # 6. Add causal signal for P-101
    from app.ingestion.observation.domain import CausalSignalFacts
    _obs_store.append(
        Observation(
            observation_id="obs_causal_1",
            trace_id="t1",
            correlation_id="c2",
            timestamp=now - datetime.timedelta(days=10),
            observation_type=ObservationType.CAUSAL_SIGNAL,
            observation_category=ObservationCategory.RELIABILITY,
            source_platform="Maximo",
            source_adapter="industrial",
            version="1.0",
            lifecycle=ObservationLifecycle.PRODUCTION,
            actors=(),
            targets=(EntityRef(id="P-101", type="asset"),),
            provenance=ObservationProvenance("Maximo", "industrial", "doc_fail_1"),
            context=ObservationContext(),
            facts=CausalSignalFacts(
                signal_id="sig_demo_1",
                asset_id="P-101",
                signal_type="LUBRICATION_DEFICIENCY",
                description="LUBRICATION_DEFICIENCY: lubrication_deficiency",
                source_document_id="doc_fail_1"
            ),
            processing_mode=ProcessingMode.LIVE,
        )
    )

    # 7. Add inspection for V-204 that is overdue (e.g. 120 days ago)
    _obs_store.append(
        Observation(
            observation_id="obs_v204",
            trace_id="t1",
            correlation_id="c3",
            timestamp=now - datetime.timedelta(days=120),
            observation_type=ObservationType.INSPECTION_EVENT,
            observation_category=ObservationCategory.INSPECTION,
            source_platform="Maximo",
            source_adapter="industrial",
            version="1.0",
            lifecycle=ObservationLifecycle.PRODUCTION,
            actors=(),
            targets=(EntityRef(id="V-204", type="asset"),),
            provenance=ObservationProvenance("Maximo", "industrial", "doc_v204_1"),
            context=ObservationContext(),
            facts=InspectionFacts(
                inspection_id="insp_v204", 
                result="SATISFACTORY",
                inspector="Alice",
            ),
            processing_mode=ProcessingMode.LIVE,
        )
    )


def get_graph_manager() -> IndustrialGraphManager:
    init_demo_state()
    assert _graph_manager is not None
    return _graph_manager


def get_observation_store() -> ObservationStore:
    init_demo_state()
    assert _obs_store is not None
    return _obs_store


def get_asset_service() -> AssetIntelligenceService:
    return AssetIntelligenceService(get_graph_manager(), get_observation_store())

def get_maintenance_service() -> MaintenanceIntelligenceService:
    return MaintenanceIntelligenceService(get_asset_service())

def get_rca_service() -> IndustrialCausalRCA:
    return IndustrialCausalRCA(get_asset_service(), get_maintenance_service())

def get_compliance_service() -> ComplianceIntelligenceService:
    return ComplianceIntelligenceService(get_asset_service())

def get_expertise_service() -> ExpertiseIntelligenceService:
    return ExpertiseIntelligenceService(get_asset_service())

def get_decision_service() -> DecisionIntelligenceService:
    return DecisionIntelligenceService(
        get_asset_service(),
        get_maintenance_service(),
        get_rca_service(),
        get_compliance_service(),
        get_expertise_service()
    )
