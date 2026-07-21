from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class WorkspaceSessionDTO_v1(BaseModel):
    user_id: str = "local_dev"
    active_repository: Optional[str] = None
    active_dataset_version: Optional[str] = None

class TraceEventDTO_v1(BaseModel):
    stage: str
    execution_time_ms: float
    decision: str
    output_summary: str
    cache_hit: bool

class GraphNodeDTO_v1(BaseModel):
    id: str
    type: str
    attributes: Dict[str, Any] = Field(default_factory=dict)

class GraphEdgeDTO_v1(BaseModel):
    source: str
    target: str
    type: str
    provenance: Optional[str] = None

class GraphResponseDTO_v1(BaseModel):
    nodes: List[GraphNodeDTO_v1]
    edges: List[GraphEdgeDTO_v1]
    total_nodes: int
    truncated: bool

class ExecutionTraceDTO_v1(BaseModel):
    query_id: str
    status: str
    answer: Optional[str] = None
    reasoning_trace: List[TraceEventDTO_v1] = Field(default_factory=list)
    total_latency_ms: float

class BenchmarkJobDTO_v1(BaseModel):
    job_id: str
    status: str
    progress: int
    metrics: Optional[Dict[str, Any]] = None
    started_at: datetime
