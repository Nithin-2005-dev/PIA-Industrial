from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class MeasurementAuditRecord:
    measurement_id: str
    action: str
    actor: str
    occurred_at: datetime
    details: dict


@dataclass(frozen=True)
class RecomputeAuditRecord:
    """Cryptographic ledger entry for historical mutations."""
    audit_id: str
    timestamp: datetime
    
    # Lineage Pointers
    old_measurement_id: str
    new_measurement_id: str
    
    # Version Tracking
    old_logic_version: str
    new_logic_version: str
    
    # Mathematical Drift
    old_value: float
    new_value: float
    percentage_drift: float
    
    # Authorization
    authorized_by: str  # e.g., 'system_auto_migration', 'admin_override'
    reason: str


class MeasurementAuditLog:

    def __init__(
        self,
    ):
        self._records = []

    def append(
        self,
        record: MeasurementAuditRecord,
    ):
        self._records.append(
            record
        )

    def log_recompute(
        self,
        record: RecomputeAuditRecord,
    ):
        self._records.append(
            record
        )

    def records_for(
        self,
        measurement_id: str,
    ) -> list[MeasurementAuditRecord]:
        return [
            record
            for record in self._records
            if record.measurement_id == measurement_id
        ]


