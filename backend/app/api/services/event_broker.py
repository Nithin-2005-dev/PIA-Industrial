import asyncio
import json
from typing import Callable, Coroutine, Any, List
from app.api.dtos.events import BaseEvent, StateChangeEvent, PlannerStartedEvent, PlannerFinishedEvent, GraphUpdatedEvent, ReasoningFinishedEvent, PresentationGeneratedEvent
from app.kernel.events import get_event_bus, Event

class EventBroker:
    def __init__(self):
        self._subscribers: List[Callable[[BaseEvent], Coroutine[Any, Any, None]]] = []
        self._kernel_bus = get_event_bus()
        
        # Subscribe to kernel events
        self._kernel_bus.subscribe("execution_stage_changed", self._on_kernel_event, is_async=True)
        self._kernel_bus.subscribe("planner_started", self._on_kernel_event, is_async=True)
        self._kernel_bus.subscribe("planner_finished", self._on_kernel_event, is_async=True)
        self._kernel_bus.subscribe("graph_updated", self._on_kernel_event, is_async=True)
        self._kernel_bus.subscribe("reasoning_finished", self._on_kernel_event, is_async=True)
        self._kernel_bus.subscribe("presentation_generated", self._on_kernel_event, is_async=True)
        self._kernel_bus.subscribe("benchmark_progress", self._on_kernel_event, is_async=True)

    def subscribe(self, callback: Callable[[BaseEvent], Coroutine[Any, Any, None]]):
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[BaseEvent], Coroutine[Any, Any, None]]):
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def publish(self, event: BaseEvent):
        for sub in self._subscribers:
            asyncio.create_task(sub(event))

    async def _on_kernel_event(self, kernel_event: Event):
        # Translate kernel events to API DTO events
        api_event = None
        session_id = kernel_event.payload.get("session_id", "unknown_session")
        query_id = kernel_event.payload.get("query_id", "unknown_query")

        if kernel_event.name == "execution_stage_changed":
            api_event = StateChangeEvent(
                session_id=session_id,
                query_id=query_id,
                previous_state=kernel_event.payload.get("old_stage", ""),
                new_state=kernel_event.payload.get("new_stage", "")
            )
        elif kernel_event.name == "planner_started":
            api_event = PlannerStartedEvent(session_id=session_id, query_id=query_id)
        elif kernel_event.name == "planner_finished":
            api_event = PlannerFinishedEvent(
                session_id=session_id,
                query_id=query_id,
                latency_ms=kernel_event.payload.get("latency_ms", 0.0),
                capabilities_selected=kernel_event.payload.get("capabilities", [])
            )
        elif kernel_event.name == "graph_updated":
            api_event = GraphUpdatedEvent(
                session_id=session_id,
                query_id=query_id,
                nodes_added=kernel_event.payload.get("nodes_added", 0),
                edges_added=kernel_event.payload.get("edges_added", 0)
            )
        elif kernel_event.name == "reasoning_finished":
            api_event = ReasoningFinishedEvent(
                session_id=session_id,
                query_id=query_id,
                latency_ms=kernel_event.payload.get("latency_ms", 0.0),
                evidence_count=kernel_event.payload.get("evidence_count", 0),
                inference_paths=kernel_event.payload.get("inference_paths", 0)
            )
        elif kernel_event.name == "presentation_generated":
            api_event = PresentationGeneratedEvent(
                session_id=session_id,
                query_id=query_id,
                latency_ms=kernel_event.payload.get("latency_ms", 0.0),
                presentation_length=kernel_event.payload.get("length", 0)
            )
        elif kernel_event.name == "benchmark_progress":
            from app.api.dtos.events import BenchmarkProgressEvent
            api_event = BenchmarkProgressEvent(
                session_id=session_id,
                job_id=kernel_event.payload.get("job_id", ""),
                progress=kernel_event.payload.get("progress", 0),
                status=kernel_event.payload.get("status", "")
            )
            
        if api_event:
            self.publish(api_event)

# Singleton instance
broker = EventBroker()

def get_event_broker() -> EventBroker:
    return broker
