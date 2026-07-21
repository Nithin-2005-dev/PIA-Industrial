import pytest

from app.kernel.graph import GraphEngine, NodeType, EdgeType
from app.kernel.models import CapabilityResult
from app.kernel.reasoning.builder import ReasoningGraphBuilder
from app.kernel.reasoning.rule_engine import RuleEngine, create_single_point_of_failure_rule
from app.kernel.reasoning.strategy import StrategyEngine
from app.kernel.reasoning.reflection import DeterministicReflectionEngine

def test_reasoning_pipeline_end_to_end():
    # 1. Initialize empty graph
    graph = GraphEngine()
    
    # 2. Mock some deterministic capability results
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
    
    # 3. Build Evidence Graph
    builder = ReasoningGraphBuilder(graph)
    builder.build_from_results(results)
    
    # Assert Evidence and Observations were created
    evidence_nodes = graph.get_all_nodes(NodeType.EVIDENCE)
    observation_nodes = graph.get_all_nodes(NodeType.OBSERVATION)
    
    assert len(evidence_nodes) == 1
    assert len(observation_nodes) == 1
    
    # 4. Initialize Reasoning Rule Engine
    rule_engine = RuleEngine(graph)
    rule_engine.register_rule(create_single_point_of_failure_rule())
    
    # 5. Execute Strategy Cycle
    strategy = StrategyEngine(graph, rule_engine)
    strategy.execute_reasoning_cycle()
    
    # Assert Inference was deterministically generated
    inference_nodes = graph.get_all_nodes(NodeType.INFERENCE)
    assert len(inference_nodes) == 1
    
    inf_node = inference_nodes[0]
    assert inf_node.properties["insight"] == "Single Point of Failure Detected"
    
    # Assert Edge Support
    support_edges = graph.get_edges(inf_node.id, direction="out", edge_type=EdgeType.SUPPORTS)
    assert len(support_edges) > 0
    
    # 6. Reflection Validation
    reflection = DeterministicReflectionEngine(graph)
    result = reflection.reflect()
    
    assert result.is_valid == True
    assert result.contradictions_found == 0
    assert len(result.unsupported_inferences) == 0
