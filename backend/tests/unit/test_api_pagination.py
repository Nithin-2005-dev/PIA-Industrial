from app.knowledge.evidence.api.api import EvidenceApi
from app.knowledge.evidence.domain import (
    Evidence, EvidenceSeverity, EvidencePriority, EvidenceStatus, 
    EvidenceLifecycle, EvidenceProvenance, EvidenceLineage, EvidenceTraceability, 
    TimeWindow, BenchmarkContext, HistoricalContext
)
from app.knowledge.evidence.core import EvidencePackage, EvidenceContext
from datetime import datetime

def make_evidence(id: str, parents: tuple[str, ...] = ()) -> Evidence:
    return Evidence(
        evidence_id=id,
        name=f"Evidence {id}",
        category="Test",
        description="test",
        severity=EvidenceSeverity.LOW,
        priority=EvidencePriority.LOW,
        status=EvidenceStatus.VALIDATED,
        confidence=1.0,
        uncertainty=0.0,
        quality=1.0,
        strength=1.0,
        supporting_measurements=(),
        contradicting_measurements=(),
        benchmark_context=BenchmarkContext(),
        historical_context=HistoricalContext(),
        time_window=TimeWindow(),
        provenance=EvidenceProvenance("test", "test", "tenant1"),
        lineage=EvidenceLineage(parent_evidence_ids=parents),
        traceability=EvidenceTraceability(),
        assumptions=(),
        limitations=(),
        validation_results=(),
        version="1",
        lifecycle=EvidenceLifecycle.VALIDATED
    )

class MockSynthesis:
    def synthesize(self, measurements, context):
        # We manually inject the package in tests, so this just returns empty
        return EvidencePackage(context=context, evidence=())

class MockRanking:
    def rank(self, evidence):
        return tuple(sorted(evidence, key=lambda x: x.evidence_id))

def test_api_pagination_search():
    api = EvidenceApi(synthesis_engine=MockSynthesis(), ranking_engine=MockRanking())
    
    # inject 500 evidence nodes
    evidence_nodes = tuple(make_evidence(f"E{i}") for i in range(500))
    package = EvidencePackage(
        tenant_id="tenant1",
        generated_at=datetime.utcnow(),
        pipeline_version="1.0",
        evidence=evidence_nodes
    )
    
    # directly set package for testing
    api._packages["tenant1"] = package
    
    # Test search pagination
    result = api.search("FIND ALL", tenant_id="tenant1", limit=100, offset=0)
    assert result["total"] == 500
    assert len(result["data"]) == 100
    assert result["data"][0].evidence_id == "E0"
    
    result = api.search("FIND ALL", tenant_id="tenant1", limit=100, offset=450)
    assert result["total"] == 500
    assert len(result["data"]) == 50
    assert result["data"][0].evidence_id == "E450"

def test_api_pagination_export():
    api = EvidenceApi(synthesis_engine=MockSynthesis(), ranking_engine=MockRanking())
    
    evidence_nodes = tuple(make_evidence(f"E{i:03d}") for i in range(500))
    package = EvidencePackage(
        tenant_id="tenant1",
        generated_at=datetime.utcnow(),
        pipeline_version="1.0",
        evidence=evidence_nodes
    )
    
    api._packages["tenant1"] = package
    
    result = api.export(tenant_id="tenant1", limit=50, offset=100)
    assert result["total"] == 500
    assert len(result["data"]) == 50
    assert result["data"][0]["id"] == "E100"
