import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass(frozen=True)
class EdgeConfidence:
    evidence_confidence: float = 1.0
    identity_confidence: float = 1.0
    extraction_confidence: float = 1.0
    relationship_confidence: float = 1.0
    
    @property
    def overall(self) -> float:
        return (
            self.evidence_confidence
            * self.identity_confidence
            * self.extraction_confidence
            * self.relationship_confidence
        )

@dataclass(frozen=True)
class EdgeProvenance:
    evidence_id: Optional[str] = None
    algorithm: str = "unknown"
    created_by: str = "system"
    timestamp: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(datetime.UTC))

@dataclass
class GraphEdge:
    """
    Directed relationship between two nodes with full provenance.
    """
    source_id: str
    target_id: str
    relationship: str
    
    confidence: EdgeConfidence = field(default_factory=EdgeConfidence)
    provenance: EdgeProvenance = field(default_factory=EdgeProvenance)
    weight: float = 1.0
    
    # Lifecycle
    created_at: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(datetime.UTC))
    updated_at: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(datetime.UTC))
    expired_at: Optional[datetime.datetime] = None
    superseded_by: Optional[str] = None
    
    properties: Dict[str, Any] = field(default_factory=dict)