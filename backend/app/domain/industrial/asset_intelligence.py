"""Asset Intelligence Domain Models.

Represents the aggregated intelligence profile of an asset.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.domain.industrial.asset import AssetCriticality, AssetStatus, RiskLevel


@dataclass(frozen=True)
class AssetTimelineEvent:
    """An event on the asset's timeline."""
    event_id: str
    event_type: str  # e.g., "INSPECTION", "MAINTENANCE", "FAILURE"
    date: datetime
    description: str
    source_document_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AssetIntelligenceProfile:
    """The complete aggregated intelligence view of an asset.
    
    This is a 360-degree view aggregating knowledge graph data,
    canonical observations, and maintenance history.
    """
    asset_id: str
    equipment_tag: str
    name: str
    asset_type: str
    
    # Hierarchy
    system: str | None = None
    subsystem: str | None = None
    plant: str | None = None
    location: str | None = None
    
    # Details
    manufacturer: str | None = None
    model: str | None = None
    
    # Status and Risk
    operational_status: AssetStatus = AssetStatus.UNKNOWN
    criticality: AssetCriticality = AssetCriticality.STANDARD
    risk_level: RiskLevel = RiskLevel.UNKNOWN
    risk_score: float = 0.0
    confidence: float = 0.0
    last_updated: datetime | None = None

    # Aggregated Lists
    documents: tuple[str, ...] = ()
    maintenance_history: tuple[str, ...] = ()
    inspection_history: tuple[str, ...] = ()
    failure_history: tuple[str, ...] = ()
    incident_history: tuple[str, ...] = ()
    
    known_failure_modes: tuple[str, ...] = ()
    components: tuple[str, ...] = ()
    operating_parameters: tuple[dict[str, Any], ...] = ()
    
    open_recommendations: tuple[str, ...] = ()
    completed_recommendations: tuple[str, ...] = ()
    
    applicable_procedures: tuple[str, ...] = ()
    applicable_regulations: tuple[str, ...] = ()
    
    responsible_personnel: tuple[str, ...] = ()
    known_experts: tuple[str, ...] = ()
    
    # Graph & Timeline
    graph_neighborhood: dict[str, Any] = field(default_factory=dict)
    timeline: tuple[AssetTimelineEvent, ...] = ()
    
    # Traceability
    evidence_links: tuple[str, ...] = ()
