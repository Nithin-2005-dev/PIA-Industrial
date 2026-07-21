import pytest

from app.kernel.graph import GraphEngine, NodeType, EdgeType
from app.kernel.models import CapabilityResult
from app.kernel.reasoning.builder import ReasoningGraphBuilder
from app.kernel.reasoning.rule_engine import RuleEngine, create_single_point_of_failure_rule
from app.kernel.reasoning.strategy import StrategyEngine
from app.kernel.intelligence.ontology import CoreOntology
from app.kernel.intelligence.translator import BusinessTranslator
from app.kernel.decision.root_cause import RootCauseAnalyzer
from app.kernel.decision.optimizer import GraphOptimizer
from app.kernel.decision.mitigation import MitigationEngine
from app.kernel.decision.allocation import ResourceAllocator
from app.kernel.resources import ResourceManager
from app.kernel.scheduler import Scheduler

def test_decision_pipeline():
    # 1. Setup Phase 2 (Reasoning)
    graph = GraphEngine()
    results = [
        CapabilityResult(
            capability_id="cap_bus_factor",
            status="SUCCESS",
            confidence=1.0,
            summary="Bus factor is 1 for critical module",
            evidence_ids=[],
            raw_output={"bus_factor": 1},
            normalized_output={},
            warnings=[],
            recommendations=[],
            metadata={},
            execution_time_ms=10.0
        )
    ]
    
    builder = ReasoningGraphBuilder(graph)
    builder.build_from_results(results)
    
    rule_engine = RuleEngine(graph)
    rule_engine.register_rule(create_single_point_of_failure_rule())
    
    strategy = StrategyEngine(graph, rule_engine)
    strategy.execute_reasoning_cycle()
    
    # 2. Setup Phase 3 (Intelligence)
    ontology = CoreOntology()
    translator = BusinessTranslator(graph, ontology)
    translator.translate_inferences_to_impact()
    
    # Assert Phase 3 produced an IMPACT
    impacts = graph.get_all_nodes(NodeType.IMPACT)
    assert len(impacts) == 1
    
    # 3. Decision Phase 4
    
    # A. Root Cause Analysis
    rc_analyzer = RootCauseAnalyzer(graph)
    rc_analyzer.analyze_root_causes()
    
    root_causes = graph.get_all_nodes(NodeType.ROOT_CAUSE)
    assert len(root_causes) == 1
    rc_node = root_causes[0]
    
    # Assert causality edge (Root Cause -> Impact)
    causes_edges = graph.get_edges(rc_node.id, direction="out", edge_type=EdgeType.CAUSES)
    assert len(causes_edges) == 1
    assert causes_edges[0].target_id == impacts[0].id
    
    # B. Graph Optimization
    optimizer = GraphOptimizer(graph)
    optimizer.optimize()
    
    assert "leverage_score" in rc_node.properties
    assert rc_node.properties["leverage_score"] == 1
    
    # C. Mitigation Engine
    mitigation = MitigationEngine(graph)
    mitigation.generate_mitigations()
    
    recommendations = graph.get_all_nodes(NodeType.RECOMMENDATION)
    assert len(recommendations) == 1
    rec_node = recommendations[0]
    assert rec_node.properties["status"] == "PENDING_ALLOCATION"
    assert "Review system architecture." in rec_node.properties["action"]
    
    # Assert mitigation edge (Recommendation -> Root Cause)
    mitigates_edges = graph.get_edges(rec_node.id, direction="out", edge_type=EdgeType.MITIGATES)
    assert len(mitigates_edges) == 1
    assert mitigates_edges[0].target_id == rc_node.id
    
    # D. Resource Allocation
    resources = ResourceManager()
    scheduler = Scheduler()
    allocator = ResourceAllocator(graph, resources, scheduler)

    
    allocator.allocate_mitigations()
    
    assert rec_node.properties["status"] == "ALLOCATED"
    assert "job_id" in rec_node.properties
    
    # Verify Job is in scheduler
    job_id = rec_node.properties["job_id"]
    assert job_id in scheduler._jobs
    assert scheduler._jobs[job_id].capability_id == "cap_auto_mitigate"
