"""Tests for M67 - Counterfactual Maintenance Simulation."""
from __future__ import annotations

from app.domain.industrial.asset import AssetCriticality, AssetStatus, RiskLevel
from app.domain.industrial.asset_intelligence import AssetIntelligenceProfile
from app.intelligence.legacy.industrial_simulation import CounterfactualMaintenanceEngine


class TestIndustrialSimulation:
    def test_simulate_delay(self):
        engine = CounterfactualMaintenanceEngine()
        
        # Baseline profile with low risk
        profile = AssetIntelligenceProfile(
            asset_id="P-101",
            equipment_tag="P-101",
            name="Main Pump",
            asset_type="Pump",
            risk_score=0.20,
            risk_level=RiskLevel.LOW,
        )
        
        # Simulate 30 day delay
        result = engine.simulate_delay(profile, 30)
        
        assert result["baseline_risk"] == 0.20
        assert result["counterfactual_risk"] == 0.50  # +0.30
        assert result["risk_delta"] == 0.30
        assert result["recommendation_priority"] == "CRITICAL"
        assert result["counterfactual_risk_level"] == "MEDIUM"
