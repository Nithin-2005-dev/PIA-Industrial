from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.knowledge.evidence.domain import EvidenceLifecycle
from app.knowledge.evidence.domain import EvidenceSeverity


class EvidenceRuleOperator(Enum):
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    EQ = "=="


@dataclass(frozen=True)
class EvidenceRule:
    id: str
    measurement_id: str
    operator: EvidenceRuleOperator
    threshold: float
    weight: float = 1.0
    explanation: str = ""
    field_source: str = "value"

    def matches(
        self,
        ref: Any,
    ) -> bool:
        value = ref.value
        if self.field_source == "percentile" and ref.calibration and ref.calibration.percentile is not None:
            value = ref.calibration.percentile
        elif self.field_source == "robust_z" and ref.calibration and ref.calibration.robust_z is not None:
            value = ref.calibration.robust_z
        elif self.field_source == "z_score" and ref.calibration and ref.calibration.z_score is not None:
            value = ref.calibration.z_score

        if self.operator == EvidenceRuleOperator.GT:
            return value > self.threshold
        if self.operator == EvidenceRuleOperator.GTE:
            return value >= self.threshold
        if self.operator == EvidenceRuleOperator.LT:
            return value < self.threshold
        if self.operator == EvidenceRuleOperator.LTE:
            return value <= self.threshold
        return value == self.threshold


@dataclass(frozen=True)
class EvidenceDefinition:
    id: str
    name: str
    category: str
    description: str
    semantic_meaning: str
    triggering_conditions: tuple[EvidenceRule, ...]
    required_measurements: tuple[str, ...]
    optional_measurements: tuple[str, ...]
    synthesis_rules: tuple[str, ...]
    confidence_strategy: str
    validation_rules: tuple[str, ...]
    interpretation: str
    standards_references: tuple[str, ...]
    business_interpretation: str
    known_limitations: tuple[str, ...]
    version_history: tuple[str, ...]
    severity: EvidenceSeverity
    rule_reliability: float = 0.85
    assumptions: tuple[str, ...] = ()
    lifecycle: EvidenceLifecycle = EvidenceLifecycle.PRODUCTION
    metadata: Mapping[str, Any] = field(default_factory=dict)

