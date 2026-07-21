import dataclasses
from typing import Any, Dict, Optional

from app.kernel.events import EventBus
from app.kernel.graph import GraphEngine
from app.kernel.registry import CapabilityRegistry
from app.kernel.resources import ResourceManager
from app.kernel.scheduler import Scheduler
from app.kernel.models import RepositoryMemory # Assuming this exists or we can mock it for now

@dataclasses.dataclass
class UserContext:
    user_id: str
    role: str

@dataclasses.dataclass
class PermissionContext:
    allowed_domains: list[str]
    allowed_capabilities: list[str]

@dataclasses.dataclass
class ExecutionContext:
    """
    The unified runtime context passed to all kernel services.
    Eliminates massive dependency injection arrays.
    """
    session_id: str
    user: UserContext
    permissions: PermissionContext
    configuration: Dict[str, Any]
    
    # Kernel Subsystems
    events: EventBus
    resources: ResourceManager
    registry: CapabilityRegistry
    scheduler: Scheduler
    graph: GraphEngine
    
    # State
    memory: RepositoryMemory
    cache: Dict[str, Any] = dataclasses.field(default_factory=dict)

    @classmethod
    def create_default(cls, session_id: str, memory: RepositoryMemory) -> "ExecutionContext":
        """Helper to instantiate a standard context."""
        return cls(
            session_id=session_id,
            user=UserContext(user_id="system", role="admin"),
            permissions=PermissionContext(allowed_domains=["*"], allowed_capabilities=["*"]),
            configuration={},
            events=EventBus(),
            resources=ResourceManager(),
            registry=CapabilityRegistry(),
            scheduler=Scheduler(),
            graph=GraphEngine(),
            memory=memory
        )
