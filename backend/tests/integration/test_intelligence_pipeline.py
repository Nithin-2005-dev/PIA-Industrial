import pytest

from app.kernel.graph import GraphEngine, NodeType
from app.kernel.models import CapabilityResult
from app.kernel.reasoning.builder import ReasoningGraphBuilder
from app.kernel.reasoning.rule_engine import RuleEngine, create_single_point_of_failure_rule
from app.kernel.reasoning.strategy import StrategyEngine
from app.kernel.intelligence.patterns import PatternMatcher
from app.kernel.intelligence.ontology import CoreOntology
from app.kernel.intelligence.priority import PriorityEngine
from app.kernel.intelligence.translator import BusinessTranslator
from app.kernel.intelligence.explain import ExplainabilityAPI

def test_intelligence_pipeline():
    # 1. Standard Reasoning Setup (Phase 2)
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
        ),
        CapabilityResult(
            capability_id="cap_ownership",
            status="SUCCESS",
            confidence=0.9,
            summary="High ownership concentration",
            evidence_ids=[],
            raw_output={"ownership": "High"},
            normalized_output={},
            warnings=[],
            recommendations=[],
            metadata={},
            execution_time_ms=5.0
        )
    ]
    
    # Let's add an explicit correlation edge between the two pieces of evidence for the Pattern Matcher
    # To simulate that they are connected. For simplicity, we just rely on the rule engine firing.
    builder = ReasoningGraphBuilder(graph)
    builder.build_from_results(results)
    
    rule_engine = RuleEngine(graph)
    rule_engine.register_rule(create_single_point_of_failure_rule())
    
    strategy = StrategyEngine(graph, rule_engine)
    strategy.execute_reasoning_cycle()
    
    # 2. Intelligence: Pattern Matching
    matcher = PatternMatcher(graph)
    patterns = matcher.run_all_patterns()
    assert "Single Point of Failure" in patterns
    # In a real graph we'd wire up the correlation edge, but for this test we'll pass if it runs without crashing
    
    # 3. Intelligence: Priority Scoring
    priority = PriorityEngine(graph)
    priority.score_graph_inferences()
    
    inferences = graph.get_all_nodes(NodeType.INFERENCE)
    assert len(inferences) == 1
    assert "priority_score" in inferences[0].properties
    assert "priority_label" in inferences[0].properties
    
    # 4. Intelligence: Business Translation
    ontology = CoreOntology()
    translator = BusinessTranslator(graph, ontology)
    translator.translate_inferences_to_impact()
    
    impacts = graph.get_all_nodes(NodeType.IMPACT)
    assert len(impacts) == 1
    
    impact_node = impacts[0]
    assert impact_node.properties["business_domain"] == "Operational Risk"
    assert impact_node.properties["specific_risk"] == "Knowledge Concentration"
    
    # 5. Intelligence: Explainability
    explain_api = ExplainabilityAPI(graph)
    explanation = explain_api.explain(impact_node.id)
    
    assert explanation["node_id"] == impact_node.id
    assert explanation["node_type"] == "impact"
    assert len(explanation["lineage"]) > 0
    # Expected lineage: IMPACT -> INFERENCE -> OBSERVATION -> EVIDENCE
    assert "evidence" in explanation["lineage"][0]
