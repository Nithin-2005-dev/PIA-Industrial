"""Industrial failure models.

Represents failure events, failure modes, and failure causes.
These models are central to Root Cause Analysis and
Failure Intelligence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class FailureSeverity(str, Enum):
    """Severity classification of a failure event."""
    CATASTROPHIC = "CATASTROPHIC"
    MAJOR = "MAJOR"
    MODERATE = "MODERATE"
    MINOR = "MINOR"
    NEGLIGIBLE = "NEGLIGIBLE"


class FailureConsequence(str, Enum):
    """Consequence category of a failure."""
    SAFETY = "SAFETY"
    ENVIRONMENTAL = "ENVIRONMENTAL"
    PRODUCTION = "PRODUCTION"
    MAINTENANCE = "MAINTENANCE"
    QUALITY = "QUALITY"
    NONE = "NONE"


# ---------------------------------------------------------------------------
# Failure Events
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FailureEvent:
    """A specific failure event that occurred on an asset.

    This is an immutable fact — something that has been observed
    or reported. It links to the asset, the failure mode, and
    the source evidence.
    """
    id: str
    asset_id: str
    equipment_tag: str | None = None
    description: str = ""
    failure_date: datetime | None = None
    detected_date: datetime | None = None
    severity: FailureSeverity = FailureSeverity.MODERATE
    consequence: FailureConsequence = FailureConsequence.PRODUCTION
    failure_mode_id: str | None = None
    failure_cause_id: str | None = None
    downtime_hours: float | None = None
    production_loss: float | None = None
    repair_cost: float | None = None
    source_document_id: str | None = None
    source_incident_id: str | None = None
    resolution: str | None = None
    resolved_date: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FailureMode:
    """A failure mode — HOW something fails.

    Examples: bearing seizure, seal leak, impeller erosion,
    corrosion, fatigue crack, electrical short.
    """
    id: str
    name: str                                   # e.g., "Bearing Seizure"
    category: str | None = None                 # e.g., "Mechanical", "Electrical", "Instrumentation"
    description: str = ""
    typical_causes: tuple[str, ...] = ()        # common cause descriptions
    typical_indicators: tuple[str, ...] = ()    # what to look for
    applicable_equipment_types: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FailureCause:
    """A failure cause — WHY something failed.

    Examples: lubrication degradation, misalignment,
    operating beyond design limits, corrosion, fatigue.
    """
    id: str
    name: str                                   # e.g., "Lubrication Degradation"
    category: str | None = None                 # e.g., "Wear", "Corrosion", "Overload", "Design"
    description: str = ""
    parent_cause_id: str | None = None          # for causal chains
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Failure Pattern (derived intelligence, not raw data)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FailurePattern:
    """A detected pattern of repeated failures.

    This is an intelligence artifact — it is derived from
    analyzing multiple FailureEvents and their relationships.
    """
    id: str
    pattern_name: str                           # e.g., "Recurring Bearing Failures in Centrifugal Pumps"
    description: str = ""
    affected_asset_ids: tuple[str, ...] = ()
    failure_mode_id: str | None = None
    failure_cause_id: str | None = None
    occurrence_count: int = 0
    first_occurrence: datetime | None = None
    last_occurrence: datetime | None = None
    mean_time_between_failures: float | None = None  # in days
    trend_direction: str = "STABLE"             # "INCREASING", "STABLE", "DECREASING"
    precursor_indicators: tuple[str, ...] = ()  # warning signs that precede this pattern
    evidence_ids: tuple[str, ...] = ()
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FailureTimeline:
    """A chronological sequence of events leading to a failure.

    Used for RCA visualization — shows the chain of events
    that preceded and contributed to a failure.
    """
    failure_event_id: str
    asset_id: str
    events: tuple[TimelineEvent, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TimelineEvent:
    """A single event in a failure timeline."""
    event_id: str
    event_type: str                             # "inspection", "maintenance", "failure", "recommendation", "parameter_change"
    description: str = ""
    timestamp: datetime | None = None
    source_document_id: str | None = None
    significance: str = "INFO"                  # "INFO", "WARNING", "CRITICAL"
    metadata: dict[str, Any] = field(default_factory=dict)
