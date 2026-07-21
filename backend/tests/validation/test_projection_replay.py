import pytest
import asyncio
from app.projections.graph_replay import KnowledgeGraphReplayEngine
from app.projections.knowledge_graph_builder import KnowledgeGraphProjectionBuilder

def test_graph_replay():
    # Build a projection
    builder = KnowledgeGraphProjectionBuilder()
    proj = builder.build_projection()
    
    # Replay it
    engine = KnowledgeGraphReplayEngine()
    report = engine.replay(proj.projection_id)
    
    assert report["match"] is True, f"Replay failed! Diverged stage: {report['diverged_stage']}"
    assert report["actual_projection_hash"] == proj.projection_hash
