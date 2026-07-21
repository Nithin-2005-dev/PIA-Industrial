from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class BaseEvent(BaseModel):
    session_id: str
    query_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class StateChangeEvent(BaseEvent):
    event_type: str = "StateChange"
    previous_state: str
    new_state: str

class PlannerStartedEvent(BaseEvent):
    event_type: str = "PlannerStarted"

class PlannerFinishedEvent(BaseEvent):
    event_type: str = "PlannerFinished"
    latency_ms: float
    capabilities_selected: list[str]

class CapabilityStartedEvent(BaseEvent):
    event_type: str = "CapabilityStarted"
    capability_name: str

class CapabilityFinishedEvent(BaseEvent):
    event_type: str = "CapabilityFinished"
    capability_name: str
    latency_ms: float
    confidence: float
    rules_fired: int

class GraphUpdatedEvent(BaseEvent):
    event_type: str = "GraphUpdated"
    nodes_added: int
    edges_added: int

class ReasoningFinishedEvent(BaseEvent):
    event_type: str = "ReasoningFinished"
    latency_ms: float
    evidence_count: int
    inference_paths: int

class PresentationGeneratedEvent(BaseEvent):
    event_type: str = "PresentationGenerated"
    latency_ms: float
    presentation_length: int

class BenchmarkProgressEvent(BaseEvent):
    event_type: str = "BenchmarkProgress"
    job_id: str
    progress: int
    status: str
