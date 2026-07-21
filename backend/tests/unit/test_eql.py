import pytest
from uuid import uuid4
from datetime import datetime

from app.knowledge.evidence.query.eql import EqlParser, EqlEngine, EqlQuery
from app.knowledge.evidence.domain import (
    Evidence,
    EvidenceSeverity,
    EvidencePriority,
    EvidenceStatus,
    EvidenceLifecycle,
    BenchmarkContext,
    HistoricalContext,
    TimeWindow,
    EvidenceProvenance,
    EvidenceLineage,
    EvidenceTraceability
)

def _create_mock_evidence(tenant_id: str, name: str) -> Evidence:
    return Evidence(
        evidence_id=str(uuid4()),
        name=name,
        category="test",
        description="test evidence",
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
        provenance=EvidenceProvenance(
            source_layer="test",
            generated_by="test",
            tenant_id=tenant_id
        ),
        lineage=EvidenceLineage(),
        traceability=EvidenceTraceability(),
        assumptions=(),
        limitations=(),
        validation_results=(),
        version="1.0",
        lifecycle=EvidenceLifecycle.PRODUCTION
    )

def test_eql_tenant_isolation():
    engine = EqlEngine()
    parser = EqlParser()
    
    # Mix of evidence from Tenant A and Tenant B
    evidence_a = _create_mock_evidence("tenant_a", "Evidence A")
    evidence_b = _create_mock_evidence("tenant_b", "Evidence B")
    
    evidence_list = (evidence_a, evidence_b)
    
    # Tenant A executes a wildcard query
    query = parser.parse("FIND ALL", tenant_id="tenant_a")
    results = engine.query(evidence_list, query)
    
    # Must only return Tenant A's evidence
    assert len(results) == 1
    assert results[0].name == "Evidence A"
    assert results[0].provenance.tenant_id == "tenant_a"

