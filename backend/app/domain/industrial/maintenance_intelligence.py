"""Maintenance & Failure Intelligence Domain Models.

Canonical outputs for deterministic pattern detection over
an asset's maintenance and failure history.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class FailurePattern:
    """A detected pattern of failures for an asset or class."""
    pattern_id: str
    asset_id: str
    failure_mode: str
    frequency_days: float | None = None
    occurrences: int = 0
    confidence: float = 0.0
    supporting_events: tuple[str, ...] = ()  # Event IDs
    source_documents: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DeferredRecommendation:
    """A maintenance recommendation that has not been acted upon."""
    finding_id: str
    asset_id: str
    description: str
    recommended_date: datetime
    days_overdue: int
    severity: str | None = None
    confidence: float = 0.0
    source_document_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FailurePrecursor:
    """A sequence of events that typically precedes a failure."""
    precursor_id: str
    asset_id: str
    precursor_events: tuple[str, ...] = ()  # Event descriptions or IDs
    target_failure_mode: str = ""
    time_window_days: float | None = None
    confidence: float = 0.0
    source_documents: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MaintenanceFinding:
    """A notable finding from inspection or maintenance history."""
    finding_id: str
    asset_id: str
    finding_type: str  # e.g., "REPEATED_ANOMALY", "UNRESOLVED_ISSUE"
    description: str
    confidence: float = 0.0
    supporting_events: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
