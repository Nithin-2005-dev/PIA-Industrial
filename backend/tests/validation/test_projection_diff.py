import pytest
from app.infrastructure.database.models import KnowledgeGraphProjectionRecord, GlobalIdentity
from app.projections.graph_diff import KnowledgeGraphDiff

def test_graph_diff():
    v1 = KnowledgeGraphProjectionRecord(
        identity=GlobalIdentity(object_type="projection"),
        projection_id="v1",
        nodes=[{"id": "n1", "type": "DEVELOPER", "attributes": {"confidence": 0.5}}],
        edges=[{"source": "n1", "target": "n2", "type": "OWNS", "confidence": 0.5}],
        node_count=1,
        edge_count=1
    )
    v2 = KnowledgeGraphProjectionRecord(
        identity=GlobalIdentity(object_type="projection"),
        projection_id="v2",
        nodes=[
            {"id": "n1", "type": "DEVELOPER", "attributes": {"confidence": 0.9}}, 
            {"id": "n2", "type": "FILE", "attributes": {}}
        ],
        edges=[{"source": "n1", "target": "n2", "type": "OWNS", "confidence": 0.8}],
        node_count=2,
        edge_count=1
    )
    
    diff = KnowledgeGraphDiff(v1, v2).compute()
    
    assert "n2" in diff["structural_changes"]["nodes_added"]
    assert len(diff["semantic_changes"]["node_property_changes"]) == 1
    assert diff["semantic_changes"]["node_property_changes"][0]["from"]["confidence"] == 0.5
    assert diff["semantic_changes"]["node_property_changes"][0]["to"]["confidence"] == 0.9
    
    assert len(diff["semantic_changes"]["edge_confidence_changes"]) == 1
    assert diff["semantic_changes"]["edge_confidence_changes"][0]["to_confidence"] == 0.8
