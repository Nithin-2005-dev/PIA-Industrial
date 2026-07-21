import pytest
from app.kernel.graph import GraphEngine, GraphNode, NodeType, GraphEdge, EdgeType
from app.kernel.intelligence.priority import PriorityEngine, PriorityPolicy
from app.kernel.reasoning.validator import GraphValidator, GraphValidationError

def test_node_canonicalization():
    engine = GraphEngine()
    
    # Generate identical nodes
    id1 = GraphNode.generate_id(NodeType.INFERENCE, "UserModule", "rule_1")
    id2 = GraphNode.generate_id(NodeType.INFERENCE, "UserModule", "rule_1")
    
    assert id1 == id2, "Canonical ID generation is not deterministic"
    
    node1 = GraphNode(id=id1, node_type=NodeType.INFERENCE, properties={"val": 1})
    node2 = GraphNode(id=id2, node_type=NodeType.INFERENCE, properties={"val": 2})
    
    added_1 = engine.add_node(node1)
    added_2 = engine.add_node(node2)
    
    assert added_1.id == added_2.id
    assert len(engine.get_all_nodes()) == 1, "Duplicate node was not merged"

def test_priority_engine():
    engine = GraphEngine()
    policy = PriorityPolicy(weight_severity=0.4, weight_impact=0.4, weight_probability=0.2)
    pe = PriorityEngine(engine, policy)
    
    # Base = 0.9*0.4 + 0.8*0.4 + 1.0*0.2 = 0.36 + 0.32 + 0.20 = 0.88
    # Multiplier = 1.0 (confidence) * 1.0 (evidence_strength) * 1.0 (1 - 0) = 1.0
    # Score = 0.88 * 100 = 88.0
    score = pe.calculate_score(confidence=1.0, severity=0.9, impact=0.8, evidence_strength=1.0)
    assert 87.0 < score < 89.0
    assert pe.semantic_bucket(score) == "Critical"

def test_graph_validator_cycles():
    engine = GraphEngine()
    validator = GraphValidator(engine)
    
    n1 = engine.add_node(GraphNode(id="n1", node_type=NodeType.EVIDENCE, properties={}))
    n2 = engine.add_node(GraphNode(id="n2", node_type=NodeType.INFERENCE, properties={}))
    
    engine.add_edge(GraphEdge(source_id="n1", target_id="n2", edge_type=EdgeType.SUPPORTS))
    engine.add_edge(GraphEdge(source_id="n2", target_id="n1", edge_type=EdgeType.SUPPORTS))
    
    with pytest.raises(GraphValidationError, match="Cycle detected"):
        validator.validate()
