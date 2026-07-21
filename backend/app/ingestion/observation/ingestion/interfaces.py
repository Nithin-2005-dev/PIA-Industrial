from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SyncCursor:
    source_id: str
    cursor_value: str

class ICheckpointStore(ABC):
    @abstractmethod
    def get(self, source_id: str) -> Optional[SyncCursor]: ...
    
    @abstractmethod
    def update_cursor(self, source_id: str, cursor: SyncCursor) -> None: ...

class IObservationStore(ABC):
    @abstractmethod
    def append_raw(self, source_id: str, external_id: str, payload: Dict[str, Any]) -> bool:
        """Returns True if appended, False if duplicate."""
        ...
        
    @abstractmethod
    def claim_batch(self, batch_size: int = 100) -> List[Dict[str, Any]]:
        """Atomically claim a batch of events by setting status to 1."""
        ...
        
    @abstractmethod
    def mark_processed(self, row_id: int) -> None:
        """Mark an event as fully processed (status=2)."""
        ...
        
    @abstractmethod
    def append_dlq(self, payload: str, error_message: str, schema_version: str, traceback_str: Optional[str] = None) -> None:
        """Store a malformed payload into the dead letter queue."""
        ...
        
    @abstractmethod
    def reset_stale_jobs(self) -> None:
        """Reset stuck status=1 jobs back to status=0."""
        ...
