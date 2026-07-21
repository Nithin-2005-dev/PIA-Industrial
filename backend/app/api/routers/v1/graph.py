from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from app.api.dtos.v1 import GraphResponseDTO_v1, GraphNodeDTO_v1, GraphEdgeDTO_v1
from app.projections.knowledge_graph_builder import KnowledgeGraphProjectionBuilder

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])

@router.get("/latest", response_model=GraphResponseDTO_v1)
async def get_latest_graph():
    builder = KnowledgeGraphProjectionBuilder()
    graph = builder.build_projection()
    
    dto_nodes = [GraphNodeDTO_v1(id=n["id"], type=n["type"], attributes=n.get("attributes", {})) for n in graph.nodes]
    dto_edges = [GraphEdgeDTO_v1(source=e["source"], target=e["target"], type=e["type"], provenance=e.get("provenance", "")) for e in graph.edges]
    
    return GraphResponseDTO_v1(nodes=dto_nodes, edges=dto_edges, total_nodes=len(graph.nodes), truncated=False)

@router.get("/{version_id}", response_model=GraphResponseDTO_v1)
async def get_version_graph(version_id: str):
    # Retrieve specific deterministic projection from the past
    builder = KnowledgeGraphProjectionBuilder()
    graph = builder.build_projection()
    
    dto_nodes = [GraphNodeDTO_v1(id=n["id"], type=n["type"], attributes=n.get("attributes", {})) for n in graph.nodes]
    dto_edges = [GraphEdgeDTO_v1(source=e["source"], target=e["target"], type=e["type"], provenance=e.get("provenance", "")) for e in graph.edges]
    
    return GraphResponseDTO_v1(nodes=dto_nodes, edges=dto_edges, total_nodes=len(graph.nodes), truncated=False)

