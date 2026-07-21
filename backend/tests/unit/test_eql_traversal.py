from app.knowledge.evidence.query.eql import EqlParser, EqlEngine
from app.knowledge.evidence.domain import (
    Evidence, EvidenceSeverity, EvidencePriority, EvidenceStatus, 
    EvidenceLifecycle, EvidenceProvenance, EvidenceLineage, EvidenceTraceability, 
    TimeWindow, BenchmarkContext, HistoricalContext
)
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

def test_eql_traversal_cycle():
    # 1. Setup cyclic dependency A -> B -> A
    ev_a = make_evidence("A", ("B",))
    ev_b = make_evidence("B", ("A",))
    
    evidence = (ev_a, ev_b)
    
    query = EqlParser().parse("FIND 3-HOP DEPENDENCIES OF A", "tenant1")
    
    engine = EqlEngine()
    results = engine.query(evidence, query)
    
    # Cycle should not hang, should return both A and B
    result_ids = {r.evidence_id for r in results}
    assert "A" in result_ids
    assert "B" in result_ids

def test_eql_traversal_depth_limit():
    # 1. Setup deep dependency A -> B -> C -> D -> E -> F -> G -> H
    ev_a = make_evidence("A", ("B",))
    ev_b = make_evidence("B", ("C",))
    ev_c = make_evidence("C", ("D",))
    ev_d = make_evidence("D", ("E",))
    ev_e = make_evidence("E", ("F",))
    ev_f = make_evidence("F", ("G",))
    ev_g = make_evidence("G", ("H",))
    ev_h = make_evidence("H", ())
    
    evidence = (ev_a, ev_b, ev_c, ev_d, ev_e, ev_f, ev_g, ev_h)
    
    # Try 100 hops, it should be clamped to 5 by parser.
    # So max depth reachable from A is 5 hops. 
    # A(0) -> B(1) -> C(2) -> D(3) -> E(4) -> F(5). G(6) and H(7) should not be reached.
    query = EqlParser().parse("FIND 100-HOP DEPENDENCIES OF A", "tenant1")
    
    engine = EqlEngine()
    results = engine.query(evidence, query)
    
    result_ids = {r.evidence_id for r in results}
    
    assert "A" in result_ids
    assert "B" in result_ids
    assert "F" in result_ids
    assert "G" not in result_ids # Depth clamped to 5
    assert "H" not in result_ids
