import pytest
from app.knowledge.evidence.graph.filters import OntologicalStopWordFilter
from app.knowledge.evidence.graph.builder import EvidenceGraphBuilder
from app.knowledge.evidence.graph.graph import LocalMemoryGraphStore
from app.knowledge.evidence.domain import Evidence, EvidenceMeasurementRef, EvidenceStatus, EvidenceSeverity, EvidencePriority, EvidenceLifecycle, TimeWindow, EvidenceProvenance, EvidenceLineage, EvidenceTraceability, BenchmarkContext, HistoricalContext
from app.knowledge.evidence.core import EvidencePackage
from datetime import datetime, UTC

def test_ontological_stop_words():
    # 1. Setup the filter and builder
    filter = OntologicalStopWordFilter()
    store = LocalMemoryGraphStore()
    builder = EvidenceGraphBuilder(store, filter)
    
    # 2. Assert direct filter logic
    assert filter.should_drop("package.json") is True
    assert filter.should_drop("yarn.lock") is True
    assert filter.should_drop("README.md") is True
    assert filter.should_drop(".gitignore") is True
    
    assert filter.should_drop("auth_router.py") is False
    assert filter.should_drop("main.go") is False
    assert filter.should_drop("PaymentService.java") is False
    
    # 3. Create a mock EvidencePackage with a God Node target
    ref1 = EvidenceMeasurementRef(
        id="m_1",
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
        metadata={"target": "yarn.lock", "actor": "Dev_A", "z_score": 3.2}
    )
    
    ref2 = EvidenceMeasurementRef(
        id="m_2",
        definition_id="def_2",
        name="Code_Complexity",
        value=5.0,
        confidence=1.0,
        uncertainty_variance=0.0,
        quality_score=1.0,
        source_system="git",
        tenant_id="t1",
        timestamp=datetime.now(UTC),
        validation_status="passed",
        metadata={"target": "auth_router.py", "actor": "Dev_B", "z_score": 2.5}
    )
    
    evidence = Evidence(
        evidence_id="e_1",
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
        supporting_measurements=(ref1, ref2),
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
        metadata={}
    )
    
    package = EvidencePackage(
        tenant_id="t1",
        generated_at=datetime.now(UTC),
        pipeline_version="v1",
        evidence=(evidence,),
        metadata={}
    )
    
    # 4. Build graph
    builder.build(package)
    
    # 5. Assert edges
    edges = store.edges()
    
    # Only auth_router.py should have an AUTHORED edge from Dev_B.
    # yarn.lock should be entirely missing.
    authored_edges = [e for e in edges if e.relationship.value == "authored"]
    
    assert len(authored_edges) == 1, "Only one AUTHORED edge should exist"
    assert authored_edges[0].source_id == "Dev_B"
    assert authored_edges[0].target_id == "auth_router.py"
