from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.knowledge.evidence.domain import Evidence


@dataclass(frozen=True)
class EvidencePackage:
    tenant_id: str | None
    generated_at: datetime
    pipeline_version: str
    evidence: tuple[Evidence, ...]
    rejected_count: int = 0
    audit_events: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def for_expertise(
        self,
    ) -> tuple[Evidence, ...]:
        return tuple(
            item
            for item in self.evidence
            if item.is_valid_for_expertise()
        )

