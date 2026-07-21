"""Industrial asset hierarchy models.

Represents the physical asset hierarchy from Plant down to Component.
All models are immutable. IDs are string-based for flexibility
(plants may use different tagging conventions).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AssetStatus(str, Enum):
    """Operational status of an asset."""
    OPERATIONAL = "OPERATIONAL"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    UNDER_MAINTENANCE = "UNDER_MAINTENANCE"
    SHUTDOWN = "SHUTDOWN"
    DECOMMISSIONED = "DECOMMISSIONED"
    STANDBY = "STANDBY"
    UNKNOWN = "UNKNOWN"


class AssetCriticality(str, Enum):
    """Criticality classification for maintenance prioritization."""
    SAFETY_CRITICAL = "SAFETY_CRITICAL"
    PRODUCTION_CRITICAL = "PRODUCTION_CRITICAL"
    IMPORTANT = "IMPORTANT"
    STANDARD = "STANDARD"
    LOW = "LOW"


class RiskLevel(str, Enum):
    """Risk assessment level."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NEGLIGIBLE = "NEGLIGIBLE"
    UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------------------------
# Physical Hierarchy
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Plant:
    """Top-level organizational unit — a physical plant or site."""
    id: str
    name: str
    location: str | None = None
    operator: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Facility:
    """A facility within a plant."""
    id: str
    name: str
    plant_id: str
    facility_type: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Area:
    """A physical area within a facility."""
    id: str
    name: str
    facility_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class System:
    """A functional system (e.g., Cooling Water System)."""
    id: str
    name: str
    area_id: str | None = None
    plant_id: str | None = None
    system_type: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Subsystem:
    """A subsystem within a system."""
    id: str
    name: str
    system_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Asset:
    """A physical asset or piece of equipment.

    This is the central entity in PIA Industrial.
    Represents a specific piece of equipment at a specific location.
    """
    id: str
    name: str
    equipment_tag: str                          # e.g., "P-101"
    asset_type: str                             # e.g., "Centrifugal Pump"
    system_id: str | None = None
    subsystem_id: str | None = None
    area_id: str | None = None
    plant_id: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    install_date: datetime | None = None
    status: AssetStatus = AssetStatus.UNKNOWN
    criticality: AssetCriticality = AssetCriticality.STANDARD
    risk_level: RiskLevel = RiskLevel.UNKNOWN
    risk_score: float = 0.0
    risk_confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Equipment:
    """Alias for Asset — used where the term 'equipment' is preferred.

    In practice, Asset and Equipment are often synonymous.
    This exists for ontology completeness.
    """
    id: str
    name: str
    equipment_tag: str
    equipment_type: str
    asset_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Component:
    """A component within an asset (e.g., bearing, seal, impeller)."""
    id: str
    name: str
    component_type: str                         # e.g., "Bearing", "Seal", "Impeller"
    asset_id: str
    manufacturer: str | None = None
    model: str | None = None
    install_date: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EquipmentTag:
    """An equipment tag reference used for entity resolution.

    Equipment tags are the primary identifier in industrial plants
    (e.g., P-101, V-204, C-301).
    """
    tag: str                                    # e.g., "P-101"
    asset_id: str | None = None                 # resolved asset
    description: str | None = None
    tag_format: str | None = None               # e.g., "ISA", "KKS", "custom"
    confidence: float = 1.0


@dataclass(frozen=True)
class Manufacturer:
    """An equipment manufacturer or OEM."""
    id: str
    name: str
    country: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OperatingParameter:
    """An operating parameter or measurement reading for an asset."""
    id: str
    asset_id: str
    parameter_name: str                         # e.g., "vibration", "temperature", "pressure"
    value: float
    unit: str                                   # e.g., "mm/s", "°C", "bar"
    recorded_at: datetime | None = None
    normal_range_low: float | None = None
    normal_range_high: float | None = None
    source_document_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_abnormal(self) -> bool:
        """Check if the value is outside normal range."""
        if self.normal_range_low is not None and self.value < self.normal_range_low:
            return True
        if self.normal_range_high is not None and self.value > self.normal_range_high:
            return True
        return False
