"""Industrial compliance models.

Represents regulations, requirements, and compliance status.
Supports the Compliance Intelligence engine.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ComplianceStatus(str, Enum):
    """Compliance assessment status.

    Important distinction:
    - MISSING_EVIDENCE means "we cannot find evidence" (may still be compliant)
    - NON_COMPLIANT means "evidence confirms non-compliance"
    These are NOT the same.
    """
    COMPLIANT = "COMPLIANT"
    PARTIALLY_COMPLIANT = "PARTIALLY_COMPLIANT"
    MISSING_EVIDENCE = "MISSING_EVIDENCE"
    OVERDUE = "OVERDUE"
    NON_COMPLIANT = "NON_COMPLIANT"
    UNKNOWN = "UNKNOWN"


class RequirementType(str, Enum):
    """Type of regulatory or procedural requirement."""
    INSPECTION = "INSPECTION"
    MAINTENANCE = "MAINTENANCE"
    TESTING = "TESTING"
    DOCUMENTATION = "DOCUMENTATION"
    TRAINING = "TRAINING"
    CALIBRATION = "CALIBRATION"
    CERTIFICATION = "CERTIFICATION"
    REPORTING = "REPORTING"
    GENERAL = "GENERAL"


class RequirementSource(str, Enum):
    """Source of the requirement."""
    REGULATION = "REGULATION"
    STANDARD = "STANDARD"
    OEM_RECOMMENDATION = "OEM_RECOMMENDATION"
    COMPANY_PROCEDURE = "COMPANY_PROCEDURE"
    INSURANCE = "INSURANCE"
    BEST_PRACTICE = "BEST_PRACTICE"


# ---------------------------------------------------------------------------
# Regulation & Requirement Models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Regulation:
    """A regulation or standard that applies to the facility."""
    id: str
    name: str                                   # e.g., "API 510", "OSHA 1910.119"
    issuing_body: str | None = None             # e.g., "API", "OSHA", "ASME"
    version: str | None = None
    effective_date: datetime | None = None
    description: str = ""
    source_document_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RegulatoryRequirement:
    """A specific requirement from a regulation.

    Each regulation may contain multiple requirements.
    """
    id: str
    regulation_id: str
    requirement_type: RequirementType = RequirementType.GENERAL
    description: str = ""
    applicable_asset_types: tuple[str, ...] = ()  # which equipment types this applies to
    applicable_asset_ids: tuple[str, ...] = ()    # specific assets
    required_frequency_days: int | None = None    # how often (in days)
    required_evidence: tuple[str, ...] = ()       # what evidence satisfies this
    source: RequirementSource = RequirementSource.REGULATION
    source_document_id: str | None = None
    source_section: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class InspectionRequirement:
    """A specific inspection requirement for an asset."""
    id: str
    asset_id: str
    requirement_id: str | None = None           # parent regulatory requirement
    equipment_tag: str | None = None
    inspection_type: str | None = None
    frequency_days: int = 365                   # default annual
    last_inspection_date: datetime | None = None
    next_due_date: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def days_until_due(self) -> int | None:
        """Days until next inspection is due."""
        if self.next_due_date is None:
            return None
        return (self.next_due_date - datetime.now()).days

    @property
    def is_overdue(self) -> bool:
        """Check if the inspection is overdue."""
        if self.next_due_date is None:
            return False
        return datetime.now() > self.next_due_date


@dataclass(frozen=True)
class MaintenanceRequirement:
    """A specific maintenance requirement for an asset."""
    id: str
    asset_id: str
    requirement_id: str | None = None
    equipment_tag: str | None = None
    maintenance_type: str | None = None
    frequency_days: int | None = None
    last_performed_date: datetime | None = None
    next_due_date: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Compliance Assessment
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ComplianceGap:
    """A detected compliance gap.

    Represents a specific requirement that is not being met,
    with evidence of why.
    """
    id: str
    requirement_id: str
    asset_id: str | None = None
    equipment_tag: str | None = None
    status: ComplianceStatus = ComplianceStatus.UNKNOWN
    description: str = ""
    last_evidence_date: datetime | None = None
    days_overdue: int | None = None
    evidence_ids: tuple[str, ...] = ()          # evidence that supports this assessment
    confidence: float = 0.0
    recommended_action: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ComplianceAssessment:
    """Overall compliance assessment for an asset or facility."""
    subject_id: str                             # asset_id or facility_id
    subject_type: str                           # "asset", "facility", "system"
    subject_name: str = ""
    total_requirements: int = 0
    compliant_count: int = 0
    partially_compliant_count: int = 0
    missing_evidence_count: int = 0
    overdue_count: int = 0
    non_compliant_count: int = 0
    unknown_count: int = 0
    compliance_score: float = 0.0               # [0, 1]
    gaps: tuple[ComplianceGap, ...] = ()
    assessed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
