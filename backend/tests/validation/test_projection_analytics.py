import pytest
from app.infrastructure.database.models import KnowledgeGraphProjectionRecord, GlobalIdentity
from app.projections.graph_analytics import KnowledgeGraphAnalytics

def test_graph_analytics():
    v1 = KnowledgeGraphProjectionRecord(
        identity=GlobalIdentity(object_type="projection"),
        projection_id="v1",
        nodes=[
            {"id": "n1", "type": "DEVELOPER", "attributes": {"confidence": 0.5}},
            {"id": "n2", "type": "FILE", "attributes": {}},
            {"id": "n3", "type": "FILE", "attributes": {}},
            {"id": "n4", "type": "FILE", "attributes": {}}
        ],
        edges=[
            {"source": "n1", "target": "n2", "type": "OWNS", "confidence": 0.5},
            {"source": "n1", "target": "n3", "type": "OWNS", "confidence": 0.5},
            {"source": "n4", "target": "n2", "type": "OWNS", "confidence": 0.5},
        ],
        node_count=4,
        edge_count=3
    )
    
    analytics = KnowledgeGraphAnalytics(v1)
    
    # 1. Build Time
    bt = analytics.compute_build_time_analytics()
    assert bt["components"] == 1
    assert "average_degree" in bt
    assert bt["degree_distribution"]["2-5"] > 0
    
    # 2. Background Time
    bg = analytics.compute_background_analytics()
    assert "communities" in bg
    assert bg["diameter_of_largest_component"] >= 1
