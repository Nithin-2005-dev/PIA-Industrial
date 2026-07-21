"""Industrial document models.

Represents the document hierarchy and provenance for industrial documents.
Every piece of extracted information must preserve its provenance
for citation-grounded answers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DocumentType(str, Enum):
    """Classification of industrial document types."""
    OEM_MANUAL = "OEM_MANUAL"
    MAINTENANCE_MANUAL = "MAINTENANCE_MANUAL"
    INSPECTION_REPORT = "INSPECTION_REPORT"
    MAINTENANCE_WORK_ORDER = "MAINTENANCE_WORK_ORDER"
    INCIDENT_REPORT = "INCIDENT_REPORT"
    NEAR_MISS_REPORT = "NEAR_MISS_REPORT"
    AUDIT_FINDING = "AUDIT_FINDING"
    QUALITY_NON_CONFORMANCE = "QUALITY_NON_CONFORMANCE"
    PROCEDURE = "PROCEDURE"
    SOP = "SOP"
    DRAWING = "DRAWING"
    PID = "PID"
    REGULATION = "REGULATION"
    SPECIFICATION = "SPECIFICATION"
    DATASHEET = "DATASHEET"
    MAINTENANCE_HISTORY = "MAINTENANCE_HISTORY"
    SENSOR_EXPORT = "SENSOR_EXPORT"
    EMAIL = "EMAIL"
    SPREADSHEET = "SPREADSHEET"
    GENERAL = "GENERAL"
    UNKNOWN = "UNKNOWN"


class DocumentFormat(str, Enum):
    """Source file format."""
    PDF = "PDF"
    PDF_SCANNED = "PDF_SCANNED"
    CSV = "CSV"
    XLSX = "XLSX"
    DOCX = "DOCX"
    TXT = "TXT"
    JSON = "JSON"
    IMAGE = "IMAGE"
    UNKNOWN = "UNKNOWN"


class ExtractionMethod(str, Enum):
    """How information was extracted from the document."""
    TEXT_EXTRACTION = "TEXT_EXTRACTION"
    OCR = "OCR"
    TABLE_PARSE = "TABLE_PARSE"
    STRUCTURED_PARSE = "STRUCTURED_PARSE"
    LLM_EXTRACTION = "LLM_EXTRACTION"
    MANUAL = "MANUAL"


class DocumentStatus(str, Enum):
    """Processing status of a document."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    DUPLICATE = "DUPLICATE"


# ---------------------------------------------------------------------------
# Core Document Models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DocumentProvenance:
    """Provenance for any piece of information extracted from a document.

    This is the foundation of citation-grounded answers.
    Every extracted entity, relationship, and fact carries this.
    """
    document_id: str
    document_name: str
    document_type: str
    page_number: int | None = None
    section: str | None = None
    chunk_id: str | None = None
    source_text: str | None = None
    extraction_method: str = ExtractionMethod.TEXT_EXTRACTION.value
    ingestion_timestamp: str | None = None
    confidence: float = 1.0
    file_hash: str | None = None


@dataclass(frozen=True)
class DocumentChunk:
    """A chunk of text extracted from a document with full provenance."""
    chunk_id: str
    document_id: str
    content: str
    page_number: int | None = None
    section: str | None = None
    chunk_index: int = 0
    token_count: int = 0
    embedding_id: str | None = None
    provenance: DocumentProvenance | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DocumentMetadata:
    """Metadata extracted from a document."""
    title: str | None = None
    author: str | None = None
    creation_date: datetime | None = None
    modification_date: datetime | None = None
    page_count: int = 0
    word_count: int = 0
    language: str | None = None
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Document:
    """An industrial document registered in the system.

    Documents are the primary source of information in PIA Industrial.
    They are ingested, parsed, chunked, and their entities are extracted
    to build the knowledge graph.
    """
    document_id: str
    name: str
    document_type: DocumentType
    document_format: DocumentFormat
    file_hash: str
    file_path: str | None = None
    file_size_bytes: int = 0
    status: DocumentStatus = DocumentStatus.PENDING
    ingested_at: datetime | None = None
    doc_metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    chunks: tuple[DocumentChunk, ...] = ()
    version: str = "1.0"
    previous_version_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Specialized Document Types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class InspectionReport:
    """An inspection report for an asset."""
    report_id: str
    document_id: str
    asset_id: str | None = None
    equipment_tag: str | None = None
    inspector: str | None = None
    inspection_date: datetime | None = None
    inspection_type: str | None = None          # e.g., "visual", "ultrasonic", "vibration"
    findings: tuple[str, ...] = ()
    recommendations: tuple[str, ...] = ()
    severity: str | None = None
    next_inspection_due: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MaintenanceWorkOrder:
    """A maintenance work order."""
    work_order_id: str
    document_id: str | None = None
    asset_id: str | None = None
    equipment_tag: str | None = None
    title: str = ""
    description: str = ""
    work_type: str | None = None                # "preventive", "corrective", "predictive"
    priority: str | None = None                 # "emergency", "urgent", "normal", "low"
    status: str = "OPEN"                        # "OPEN", "IN_PROGRESS", "COMPLETED", "DEFERRED", "CANCELLED"
    requested_by: str | None = None
    assigned_to: str | None = None
    requested_date: datetime | None = None
    scheduled_date: datetime | None = None
    completed_date: datetime | None = None
    actions_taken: tuple[str, ...] = ()
    parts_used: tuple[str, ...] = ()
    labor_hours: float | None = None
    cost: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class IncidentReport:
    """An incident or failure event report."""
    incident_id: str
    document_id: str | None = None
    asset_id: str | None = None
    equipment_tag: str | None = None
    title: str = ""
    description: str = ""
    incident_date: datetime | None = None
    severity: str | None = None                 # "minor", "moderate", "major", "catastrophic"
    impact: str | None = None                   # description of operational impact
    root_cause: str | None = None
    corrective_actions: tuple[str, ...] = ()
    preventive_actions: tuple[str, ...] = ()
    reported_by: str | None = None
    investigated_by: str | None = None
    downtime_hours: float | None = None
    safety_impact: bool = False
    environmental_impact: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NearMissReport:
    """A near-miss event report."""
    near_miss_id: str
    document_id: str | None = None
    asset_id: str | None = None
    equipment_tag: str | None = None
    description: str = ""
    event_date: datetime | None = None
    potential_severity: str | None = None
    reported_by: str | None = None
    corrective_actions: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AuditFinding:
    """An audit finding."""
    finding_id: str
    document_id: str | None = None
    asset_id: str | None = None
    description: str = ""
    finding_type: str | None = None             # "observation", "minor_nc", "major_nc"
    audit_date: datetime | None = None
    auditor: str | None = None
    corrective_action_required: bool = False
    due_date: datetime | None = None
    status: str = "OPEN"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class QualityNonConformance:
    """A quality non-conformance record."""
    ncr_id: str
    document_id: str | None = None
    asset_id: str | None = None
    description: str = ""
    category: str | None = None
    detected_date: datetime | None = None
    detected_by: str | None = None
    disposition: str | None = None              # "rework", "repair", "scrap", "use_as_is"
    root_cause: str | None = None
    corrective_actions: tuple[str, ...] = ()
    status: str = "OPEN"
    metadata: dict[str, Any] = field(default_factory=dict)
