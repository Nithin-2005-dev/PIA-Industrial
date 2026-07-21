"""Tests for M66 - Industrial Causal RCA."""
from __future__ import annotations

from app.intelligence.legacy.industrial_causal_rca import IndustrialCausalRCA


class TestIndustrialCausalRCA:
    def test_run_rca(self):
        # We bypass the full pipeline to just test the Causal Engine directly on observed states
        rca = IndustrialCausalRCA(None, None) # type: ignore
        
        # Scenario: High vibration observed, which should cause bearing failure, which causes equipment failure
        observed_nodes = {
            "high_vibration": 0.9,
            "bearing_failure": 0.9,
            "equipment_failure": 1.0,
        }
        
        ctx = rca.run_rca(observed_nodes)
        
        # Check hypothesis and root cause logic
        assert len(ctx.root_causes) > 0
        
        # Primary cause should point back to high_vibration -> mechanical_wear
        primary = ctx.explanation.primary_cause
        assert primary is not None
        assert "vibration" in primary.subject.lower() or primary.mechanism_id == "mechanical_wear"
        
        # The chain should connect vibration -> bearing -> equipment
        assert len(primary.causal_chain.edges) >= 1
