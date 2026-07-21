"""Industrial personnel models.

Represents engineers, technicians, operators, and their
expertise relationships with assets and systems.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class PersonnelRole(str, Enum):
    """Role classification for industrial personnel."""
    ENGINEER = "ENGINEER"
    TECHNICIAN = "TECHNICIAN"
    OPERATOR = "OPERATOR"
    INSPECTOR = "INSPECTOR"
    SUPERVISOR = "SUPERVISOR"
    MANAGER = "MANAGER"
    SME = "SME"                                 # Subject Matter Expert
    CONTRACTOR = "CONTRACTOR"
    VENDOR = "VENDOR"


class ExpertiseLevel(str, Enum):
    """Level of expertise a person has with a subject."""
    EXPERT = "EXPERT"
    PROFICIENT = "PROFICIENT"
    COMPETENT = "COMPETENT"
    BEGINNER = "BEGINNER"
    NONE = "NONE"


# ---------------------------------------------------------------------------
# Personnel Models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Person:
    """A person involved in industrial operations.

    This is the generalized equivalent of PIA's 'Developer'.
    """
    id: str
    name: str
    role: PersonnelRole = PersonnelRole.ENGINEER
    department: str | None = None
    team: str | None = None
    plant_id: str | None = None
    email: str | None = None
    employee_id: str | None = None
    active: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Team:
    """An operational or maintenance team."""
    id: str
    name: str
    department: str | None = None
    plant_id: str | None = None
    members: tuple[str, ...] = ()               # person IDs
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Expertise Models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AssetExpertise:
    """Expertise relationship between a person and an asset.

    This is the industrial equivalent of PIA's ExpertiseEstimate.
    Expertise is INFERRED from evidence (maintenance performed,
    inspections conducted, reports authored) — NOT from job titles.
    """
    person_id: str
    asset_id: str
    expertise_score: float                      # [0, 1]
    expertise_level: ExpertiseLevel = ExpertiseLevel.NONE
    confidence: float = 0.0
    evidence_ids: tuple[str, ...] = ()          # what evidence supports this
    interaction_count: int = 0                  # number of documented interactions
    last_interaction: datetime | None = None
    expertise_areas: tuple[str, ...] = ()       # specific areas of expertise
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SystemExpertise:
    """Expertise relationship between a person and a system."""
    person_id: str
    system_id: str
    expertise_score: float
    expertise_level: ExpertiseLevel = ExpertiseLevel.NONE
    confidence: float = 0.0
    evidence_ids: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class KnowledgeConcentration:
    """Knowledge concentration metric for an asset or system.

    This is the industrial equivalent of PIA's Bus Factor.
    High concentration = knowledge cliff risk.
    """
    subject_id: str                             # asset_id or system_id
    subject_type: str                           # "asset" or "system"
    subject_name: str = ""
    total_experts: int = 0
    primary_expert_id: str | None = None
    primary_expert_name: str | None = None
    primary_expert_share: float = 0.0           # % of knowledge held by primary expert
    concentration_score: float = 0.0            # [0, 1] — higher = more concentrated = riskier
    risk_level: str = "UNKNOWN"                 # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    evidence_ids: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
