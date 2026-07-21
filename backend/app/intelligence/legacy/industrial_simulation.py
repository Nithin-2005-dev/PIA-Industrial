"""Counterfactual Maintenance Intelligence Service.

Simulates the risk impact of industrial interventions like delaying
maintenance, increasing inspections, or replacing an asset.
"""
from __future__ import annotations

import copy
import dataclasses
from typing import Any

from app.domain.industrial.asset import RiskLevel
from app.domain.industrial.asset_intelligence import AssetIntelligenceProfile
from app.intelligence.counterfactual.engine import SimulationEngine
from app.intelligence.counterfactual.models import (
    ScenarioContext,
    SimulationAssumption,
    SimulationIntervention,
    SimulationScenario,
)


@dataclasses.dataclass(frozen=True)
class MaintenanceDelayIntervention:
    """Simulates delaying maintenance on an asset."""
    
    asset_id: str
    delay_days: int
    name: str = "Delay Maintenance"

    def apply(self, context: Any) -> None:
        """Apply to an AssetIntelligenceProfile."""
        if not isinstance(context, AssetIntelligenceProfile):
            return
        
        # In a real engine, this would increase failure probability.
        # For M67 deterministic logic, we just modify the risk score directly
        # based on the delay.
        new_risk_score = min(1.0, context.risk_score + (self.delay_days * 0.01))
        
        # Because AssetIntelligenceProfile is frozen, we have to bypass it or rebuild it.
        # It's a dataclass, we can't just mutate it.
        # In `SimulationEngine._clone_context`, it uses `copy.copy()`. If it's frozen, 
        # we have to use `dataclasses.replace`.
        pass # Actual mutation handled by the engine wrapper which knows it's frozen

    def restart_stage(self) -> str:
        return "asset_intelligence"


class CounterfactualMaintenanceEngine:
    """Wraps canonical SimulationEngine for Industrial assets."""
    
    def __init__(self) -> None:
        self._sim_engine = SimulationEngine()

    def simulate_delay(self, profile: AssetIntelligenceProfile, delay_days: int) -> dict[str, Any]:
        """Simulate the effect of delaying maintenance on the asset's risk profile."""
        
        intervention = MaintenanceDelayIntervention(
            asset_id=profile.asset_id,
            delay_days=delay_days,
        )
        
        scenario = SimulationScenario(
            name=f"Delay {profile.asset_id} Maintenance by {delay_days} days",
            description="Assesses risk impact of deferred maintenance",
            assumptions=(
                SimulationAssumption("Failure probability increases linearly with delay"),
            ),
            interventions=(intervention,)
        )
        
        # 1. Clone context
        # AssetIntelligenceProfile is frozen. SimulationEngine._clone_context does `copy.copy`,
        # but we can't mutate the clone. So we just build a new profile explicitly.
        
        scenario_risk_score = min(1.0, profile.risk_score + (delay_days * 0.01))
        
        if scenario_risk_score > 0.8:
            scenario_risk_level = RiskLevel.CRITICAL
        elif scenario_risk_score > 0.6:
            scenario_risk_level = RiskLevel.HIGH
        elif scenario_risk_score > 0.4:
            scenario_risk_level = RiskLevel.MEDIUM
        else:
            scenario_risk_level = RiskLevel.LOW
            
        cloned_profile = dataclasses.replace(
            profile,
            risk_score=scenario_risk_score,
            risk_level=scenario_risk_level,
        )
        
        # 2. Compare
        delta = scenario_risk_score - profile.risk_score
        
        priority = "LOW"
        if delta > 0.2:
            priority = "CRITICAL"
        elif delta > 0.1:
            priority = "HIGH"
            
        return {
            "scenario": scenario.name,
            "baseline_risk": profile.risk_score,
            "counterfactual_risk": scenario_risk_score,
            "risk_delta": delta,
            "recommendation_priority": priority,
            "baseline_risk_level": profile.risk_level.value,
            "counterfactual_risk_level": scenario_risk_level.value,
        }
