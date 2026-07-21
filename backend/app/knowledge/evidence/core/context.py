from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class EvidenceContext:
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )
    tenant_id: str | None = None
    organization_id: str | None = None
    pipeline_version: str = "evidence.v1"
    feature_flags: Mapping[str, bool] = field(default_factory=dict)
    installed_evidence_packs: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

