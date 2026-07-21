"""Compliance Intelligence Domain Models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class InspectionRequirement:
    """A requirement for periodic inspection."""
    requirement_id: str
    asset_type: str
    regulation_id: str
    frequency_days: int
    required_inspection_type: str
    description: str


@dataclass(frozen=True)
class Regulation:
    """An industrial standard or regulation."""
    regulation_id: str
    name: str
    authority: str
    description: str


@dataclass(frozen=True)
class ComplianceGap:
    """A detected gap in compliance for an asset."""
    gap_id: str
    asset_id: str
    requirement_id: str
    status: str  # "OVERDUE", "MISSING_EVIDENCE"
    days_overdue: int | None = None
    last_inspection_date: datetime | None = None
    last_inspection_doc_id: str | None = None
    severity: str = "HIGH"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ComplianceEvidencePackage:
    """A compiled set of evidence showing compliance (or gaps)."""
    asset_id: str
    generated_at: datetime
    compliant: bool
    gaps: tuple[ComplianceGap, ...]
    supporting_documents: tuple[str, ...]
