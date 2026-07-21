"""Industrial Causal Rules for RCA Engine."""
from __future__ import annotations

from app.intelligence.causal.rules import CausalRule, RuleProvider


class IndustrialReliabilityRuleProvider(RuleProvider):
    """Causal rules linking industrial symptoms to failure modes."""

    name = "industrial_reliability"

    def rules(self) -> tuple[CausalRule, ...]:
        return (
            CausalRule(
                id="high_vibration.bearing_failure",
                cause_node="high_vibration",
                effect_node="bearing_failure",
                direction="increase",
                mechanism_id="mechanical_wear",
                rule_confidence=0.85,
                description=(
                    "High or increasing vibration is a strong causal indicator of "
                    "impending bearing failure due to mechanical wear and fatigue."
                ),
            ),
            CausalRule(
                id="high_temperature.seal_failure",
                cause_node="high_temperature",
                effect_node="seal_failure",
                direction="increase",
                mechanism_id="thermal_degradation",
                rule_confidence=0.80,
                description=(
                    "Elevated operating temperatures degrade mechanical seals "
                    "leading to premature failure and leaks."
                ),
            ),
            CausalRule(
                id="deferred_maintenance.equipment_failure",
                cause_node="deferred_maintenance",
                effect_node="equipment_failure",
                direction="increase",
                mechanism_id="preventive_maintenance_missed",
                rule_confidence=0.75,
                description=(
                    "Failing to perform recommended preventive maintenance increases "
                    "the probability of catastrophic equipment failure."
                ),
            ),
            CausalRule(
                id="bearing_failure.equipment_failure",
                cause_node="bearing_failure",
                effect_node="equipment_failure",
                direction="increase",
                mechanism_id="subsystem_cascade",
                rule_confidence=0.95,
                description=(
                    "Bearing failure inevitably leads to total equipment failure "
                    "if not immediately addressed."
                ),
            ),
        )
