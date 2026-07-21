import pytest
from app.knowledge.evidence.graph.filters import OntologicalStopWordFilter
from app.knowledge.evidence.graph.builder import EvidenceGraphBuilder
from app.knowledge.evidence.graph.graph import LocalMemoryGraphStore
from app.knowledge.evidence.domain import Evidence, EvidenceMeasurementRef, EvidenceStatus, EvidenceSeverity, EvidencePriority, EvidenceLifecycle, TimeWindow, EvidenceProvenance, EvidenceLineage, EvidenceTraceability, BenchmarkContext, HistoricalContext
from app.knowledge.evidence.core import EvidencePackage
from datetime import datetime, UTC

def _create_mock_evidence(evidence_id: str, supersedes_id: str | None, z_score: float) -> Evidence:
    ref = EvidenceMeasurementRef(
        id=f"m_{evidence_id}",
        definition_id="def_1",
        name="Code_Complexity",
        value=5.0,
        confidence=1.0,
        uncertainty_variance=0.0,
        quality_score=1.0,
        source_system="git",
        tenant_id="t1",
        timestamp=datetime.now(UTC),
        validation_status="passed",
        metadata={"target": "auth_router.py", "actor": "Dev_A", "z_score": z_score}
    )
    
    metadata = {}
    if supersedes_id:
        metadata["supersedes_id"] = supersedes_id
        
    return Evidence(
        evidence_id=evidence_id,
        name="Complexity Check",
        category="maintainability",
        description="Check",
        severity=EvidenceSeverity.LOW,
        priority=EvidencePriority.LOW,
        status=EvidenceStatus.VALIDATED,
        confidence=1.0,
        uncertainty=0.0,
        quality=1.0,
        strength=1.0,
        supporting_measurements=(ref,),
        contradicting_measurements=(),
        benchmark_context=BenchmarkContext(),
        historical_context=HistoricalContext(),
        time_window=TimeWindow(),
        provenance=EvidenceProvenance("sys", "me"),
        lineage=EvidenceLineage(),
        traceability=EvidenceTraceability(),
        assumptions=(),
        limitations=(),
        validation_results=(),
        version="v1",
        lifecycle=EvidenceLifecycle.PRODUCTION,
        metadata=metadata
    )

def test_supersession_graph_handler():
    store = LocalMemoryGraphStore()
    builder = EvidenceGraphBuilder(store)
    
    # 1. Add Initial Evidence (Z-Score 3.0)
    ev_old = _create_mock_evidence("e_old_123", None, 3.0)
    builder.build(EvidencePackage(
        tenant_id="t1", generated_at=datetime.now(UTC), pipeline_version="v1", evidence=(ev_old,), metadata={}
    ))
    
    # Assert nodes and edges exist for e_old_123
    assert len([n for n in store.nodes() if n.id == "e_old_123"]) == 1
    authored_edges = [e for e in store.edges() if e.relationship.value == "authored"]
    assert len(authored_edges) == 1
    
    # 2. Add New Evidence superseding the old one (Z-Score 1.5)
    ev_new = _create_mock_evidence("e_new_456", "e_old_123", 1.5)
    builder.build(EvidencePackage(
        tenant_id="t1", generated_at=datetime.now(UTC), pipeline_version="v1", evidence=(ev_new,), metadata={}
    ))
    
    # 3. Assert old evidence node is physically deleted
    assert len([n for n in store.nodes() if n.id == "e_old_123"]) == 0
    assert len([n for n in store.nodes() if n.id == "e_new_456"]) == 1
    
    # 4. Assert old edges connecting to the old evidence are removed (SUPPORTS, EXPLAINS)
    supports_edges = [e for e in store.edges() if e.relationship.value == "supports"]
    assert len([e for e in supports_edges if e.target_id == "e_old_123"]) == 0
    assert len([e for e in supports_edges if e.target_id == "e_new_456"]) == 1
    
    # 5. Wait, we deleted the Evidence node, but what about the AUTHORED edge?
    # Our simple remove_evidence ONLY removes edges where source or target is the Evidence Node!
    # The AUTHORED edge is between 'Dev_A' and 'auth_router.py'.
    # It will NOT be deleted by `remove_evidence(evidence_id)` because neither source nor target is the evidence_id!
    # Let's verify this behavior in the test.
    authored_edges = [e for e in store.edges() if e.relationship.value == "authored"]
    
    # We expect 2 authored edges if we didn't properly clean up the structural edges!
    # This means our removal logic in LocalMemoryGraphStore is INSUFFICIENT for structural edges!
    # We must fix this. 
    # BUT for the test, we want it to assert len == 1, meaning we properly cleaned it up.
    # Currently it will fail.
    
    assert len(authored_edges) == 1, "The superseded structural edge should have been removed!"
