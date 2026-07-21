from typing import Any, Dict, List, Optional
import dataclasses

@dataclasses.dataclass
class ResourceRequirements:
    cpu: int = 1
    memory_mb: int = 256
    needs_gpu: bool = False
    custom_resources: List[str] = dataclasses.field(default_factory=list)

class ResourceManager:
    """
    Manages abstract resources needed by capabilities (e.g. DB connections, repo instances, GPUs).
    """
    def __init__(self):
        self._available_resources: Dict[str, Any] = {}
        self._allocations: Dict[str, List[str]] = {} # Allocation ID to Resource IDs
        
    def register_resource(self, resource_id: str, resource: Any):
        self._available_resources[resource_id] = resource
        
    def allocate(self, requirements: ResourceRequirements) -> str:
        """
        Attempts to allocate resources satisfying requirements.
        Returns an allocation ID if successful, else raises ValueError.
        """
        allocation_id = f"alloc_{len(self._allocations)}"
        # Simplified resource allocation for Phase 1
        self._allocations[allocation_id] = []
        return allocation_id
        
    def release(self, allocation_id: str):
        """Releases resources tied to an allocation ID."""
        if allocation_id in self._allocations:
            del self._allocations[allocation_id]
