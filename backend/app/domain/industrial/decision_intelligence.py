"""Decision Intelligence Domain Models."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProposedIntervention:
    """A recommended action for an asset."""
    intervention_id: str
    asset_id: str
    action_type: str  # "MAINTENANCE", "INSPECTION", "REPLACEMENT", "TRAINING"
    title: str
    description: str
    estimated_cost: float
    risk_reduction_score: float  # Expected drop in risk score [0.0 - 1.0]
    compliance_impact: bool      # Does this resolve a compliance gap?


@dataclass(frozen=True)
class IndustrialInterventionPortfolio:
    """A prioritized list of interventions across assets."""
    portfolio_id: str
    interventions: tuple[ProposedIntervention, ...]
    total_estimated_cost: float
    overall_risk_reduction: float
