"""Industrial maintenance models.

Represents maintenance actions, recommendations, and
maintenance intelligence artifacts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MaintenanceType(str, Enum):
    """Type of maintenance activity."""
    PREVENTIVE = "PREVENTIVE"
    CORRECTIVE = "CORRECTIVE"
    PREDICTIVE = "PREDICTIVE"
    CONDITION_BASED = "CONDITION_BASED"
    EMERGENCY = "EMERGENCY"
    OVERHAUL = "OVERHAUL"
    MODIFICATION = "MODIFICATION"
    INSPECTION = "INSPECTION"


class MaintenancePriority(str, Enum):
    """Priority classification for maintenance actions."""
    EMERGENCY = "EMERGENCY"
    URGENT = "URGENT"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"
    DEFERRED = "DEFERRED"


class RecommendationStatus(str, Enum):
    """Status of a maintenance recommendation."""
    OPEN = "OPEN"
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DEFERRED = "DEFERRED"
    REJECTED = "REJECTED"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


# ---------------------------------------------------------------------------
# Maintenance Actions
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MaintenanceAction:
    """A maintenance action performed on an asset."""
    id: str
    asset_id: str
    equipment_tag: str | None = None
    action_type: MaintenanceType = MaintenanceType.CORRECTIVE
    description: str = ""
    performed_by: str | None = None
    performed_date: datetime | None = None
    duration_hours: float | None = None
    parts_replaced: tuple[str, ...] = ()
    findings: tuple[str, ...] = ()
    work_order_id: str | None = None
    source_document_id: str | None = None
    cost: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Inspection:
    """An inspection performed on an asset."""
    id: str
    asset_id: str
    equipment_tag: str | None = None
    inspection_type: str | None = None          # "visual", "ultrasonic", "vibration", "thermographic"
    inspector: str | None = None
    inspection_date: datetime | None = None
    findings: tuple[str, ...] = ()
    measurements: tuple[str, ...] = ()          # parameter readings taken during inspection
    result: str = "SATISFACTORY"                # "SATISFACTORY", "UNSATISFACTORY", "CONDITIONAL"
    next_due_date: datetime | None = None
    report_id: str | None = None
    source_document_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Recommendation:
    """A maintenance or engineering recommendation.

    Recommendations are critical for tracking deferred actions
    and identifying when ignored recommendations led to failures.
    """
    id: str
    asset_id: str | None = None
    equipment_tag: str | None = None
    description: str = ""
    action_required: str = ""
    priority: MaintenancePriority = MaintenancePriority.NORMAL
    status: RecommendationStatus = RecommendationStatus.OPEN
    recommended_by: str | None = None
    recommended_date: datetime | None = None
    due_date: datetime | None = None
    completed_date: datetime | None = None
    source_document_id: str | None = None
    source_inspection_id: str | None = None
    work_order_id: str | None = None            # linked work order if created
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_overdue(self) -> bool:
        """Check if the recommendation is past its due date."""
        if self.due_date is None:
            return False
        if self.status in (RecommendationStatus.COMPLETED, RecommendationStatus.CANCELLED):
            return False
        return datetime.now() > self.due_date

    @property
    def is_deferred(self) -> bool:
        """Check if the recommendation has been deferred."""
        return self.status == RecommendationStatus.DEFERRED


# ---------------------------------------------------------------------------
# Maintenance Intelligence
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MaintenanceIntervention:
    """A prioritized maintenance intervention recommendation.

    This is an intelligence artifact produced by the
    Maintenance Optimization engine.
    """
    id: str
    asset_id: str
    action: str                                 # what to do
    rationale: str                              # why to do it
    equipment_tag: str | None = None
    priority_rank: int = 0
    risk_reduction: float = 0.0                 # expected risk reduction [0, 1]
    estimated_cost: float = 0.0
    estimated_downtime_hours: float = 0.0
    urgency: MaintenancePriority = MaintenancePriority.NORMAL
    evidence_ids: tuple[str, ...] = ()
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

