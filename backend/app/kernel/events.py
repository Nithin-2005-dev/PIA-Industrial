import asyncio
import dataclasses
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

class EventPriority(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    BACKGROUND = 3

class EventType(Enum):
    SYNC = "sync"
    ASYNC = "async"
    STREAMING = "streaming"
    PERSISTENT = "persistent"

@dataclasses.dataclass(frozen=True)
class Event:
    id: str
    name: str
    event_type: EventType
    priority: EventPriority
    payload: Dict[str, Any]
    timestamp: float = dataclasses.field(default_factory=time.time)

class EventBus:
    """
    Priority-based event bus decoupling kernel components.
    Supports Sync, Async, Streaming, and Persistent events.
    """
    def __init__(self):
        self._handlers: Dict[str, List[Callable[[Event], Any]]] = {}
        self._async_handlers: Dict[str, List[Callable[[Event], Any]]] = {}
        
    def subscribe(self, event_name: str, handler: Callable[[Event], Any], is_async: bool = False):
        if is_async:
            if event_name not in self._async_handlers:
                self._async_handlers[event_name] = []
            self._async_handlers[event_name].append(handler)
        else:
            if event_name not in self._handlers:
                self._handlers[event_name] = []
            self._handlers[event_name].append(handler)

    def publish_sync(self, event: Event) -> List[Any]:
        """Publishes a synchronous event and returns all handler results immediately."""
        results = []
        if event.name in self._handlers:
            for handler in self._handlers[event.name]:
                results.append(handler(event))
        return results

    async def publish_async(self, event: Event):
        """Publishes an asynchronous event."""
        if event.name in self._async_handlers:
            tasks = [handler(event) for handler in self._async_handlers[event.name]]
            await asyncio.gather(*tasks)

    def publish(self, event_type: str, stage: str, **data):
        event = Event(
            id=str(time.time()),
            name=event_type,
            event_type=EventType.SYNC,
            priority=EventPriority.NORMAL,
            payload={'stage': stage, **data}
        )
        self.publish_sync(event)

_bus_instance = EventBus()

def get_event_bus() -> EventBus:
    return _bus_instance
