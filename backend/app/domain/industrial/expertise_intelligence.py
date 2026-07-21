"""Expertise Intelligence Domain Models."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AssetExpertise:
    """Expertise inferred for a single actor on a specific asset."""
    asset_id: str
    actor_id: str
    expertise_score: float  # 0.0 to 1.0
    evidence_count: int
    primary_role: str       # "INSPECTOR", "MAINTENANCE", "OPERATOR"
    evidence_summary: str


@dataclass(frozen=True)
class CriticalKnowledgeConcentration:
    """Industrial equivalent to Bus Factor, measuring knowledge concentration."""
    asset_id: str
    expert_count: int
    top_expert_id: str | None
    concentration_score: float  # 0.0 (distributed) to 1.0 (highly concentrated)
    risk_level: str             # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    recommendation: str
