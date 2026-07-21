from dataclasses import dataclass
from app.knowledge.evidence.domain import EvidenceSeverity
from app.knowledge.evidence.knowledge.definitions import EvidenceDefinition
from app.knowledge.evidence.knowledge.definitions import EvidenceRule
from app.knowledge.evidence.knowledge.definitions import EvidenceRuleOperator


@dataclass(frozen=True)
class MeasurementKnowledgeEntry:
    concept_id: str
    scientific_references: tuple[str, ...] = ()
    standards: tuple[str, ...] = ()
    known_limitations: tuple[str, ...] = ()
    recommended_interpretation: str | None = None
    anti_patterns: tuple[str, ...] = ()
    normalization_notes: tuple[str, ...] = ()


class MeasurementKnowledgeBase:

    def __init__(
        self,
    ):
        self._entries = {}

    def register(
        self,
        entry: MeasurementKnowledgeEntry,
    ):
        self._entries[
            entry.concept_id
        ] = entry

    def get(
        self,
        concept_id: str,
    ) -> MeasurementKnowledgeEntry | None:
        return self._entries.get(
            concept_id
        )


class EvidenceKnowledgeBase:

    def __init__(
        self,
        definitions: tuple[EvidenceDefinition, ...] = (),
    ):
        self._definitions = {
            definition.id: definition
            for definition in definitions
        }

    @classmethod
    def default(
        cls,
    ) -> "EvidenceKnowledgeBase":
        return cls(
            definitions=(
                # -----------------------------------------------------------------
                # Maintainability & Complexity
                # -----------------------------------------------------------------
                EvidenceDefinition(
                    id="file_maintenance_risk",
                    name="File Maintenance Risk",
                    category="maintainability",
                    description="File subsystem has elevated maintenance risk due to high churn.",
                    semantic_meaning="Localized area combines high change volume and complexity.",
                    triggering_conditions=(
                        EvidenceRule(
                            id="file-churn-high",
                            measurement_id="file_churn",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=0.9,
                            weight=1.0,
                            field_source="percentile",
                        ),
                    ),
                    required_measurements=("file_churn",),
                    optional_measurements=("file_complexity_delta", "file_touch_count"),
                    synthesis_rules=("all_required_measurements_present",),
                    confidence_strategy="factor_product_with_explanation",
                    validation_rules=("logical", "semantic"),
                    interpretation="Treat the affected area as a maintenance hotspot.",
                    standards_references=("ISO/IEC 25010 maintainability",),
                    business_interpretation="Sustained work here may require senior review.",
                    known_limitations=("Static change signals may miss runtime behavior.",),
                    version_history=("1.0",),
                    severity=EvidenceSeverity.HIGH,
                    rule_reliability=0.88,
                ),
                EvidenceDefinition(
                    id="high_complexity_area",
                    name="High Complexity Area",
                    category="architecture",
                    description="Code area exhibits significant control-flow complexity delta.",
                    semantic_meaning="Area introduces structural complexity risk.",
                    triggering_conditions=(
                        EvidenceRule(
                            id="complexity-high",
                            measurement_id="file_complexity_delta",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=0.95,
                            weight=1.0,
                            field_source="percentile",
                        ),
                    ),
                    required_measurements=("file_complexity_delta",),
                    optional_measurements=("patch_complexity_delta",),
                    synthesis_rules=("all_required_measurements_present",),
                    confidence_strategy="factor_product_with_explanation",
                    validation_rules=("logical",),
                    interpretation="Refactoring may be needed soon.",
                    standards_references=("ISO/IEC 25010 maintainability",),
                    business_interpretation="High defect probability.",
                    known_limitations=(),
                    version_history=("1.0",),
                    severity=EvidenceSeverity.MEDIUM,
                    rule_reliability=0.85,
                ),

                # -----------------------------------------------------------------
                # Developer Activity & Knowledge
                # -----------------------------------------------------------------
                EvidenceDefinition(
                    id="developer_velocity",
                    name="Developer Velocity",
                    category="developer",
                    description="Developer is producing changes at a high rate.",
                    semantic_meaning="Developer has frequent and significant contributions.",
                    triggering_conditions=(
                        EvidenceRule(
                            id="contribution-high",
                            measurement_id="developer_commit_frequency",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=2.0,
                            weight=1.0,
                            field_source="robust_z",
                        ),
                    ),
                    required_measurements=("developer_commit_frequency",),
                    optional_measurements=("author_code_churn", "developer_recency_score"),
                    synthesis_rules=("required_measurement_present",),
                    confidence_strategy="factor_product_with_explanation",
                    validation_rules=("logical",),
                    interpretation="Developer is actively shipping code.",
                    standards_references=(),
                    business_interpretation="High throughput contributor.",
                    known_limitations=(),
                    version_history=("1.0",),
                    severity=EvidenceSeverity.LOW,
                    rule_reliability=0.9,
                ),
                EvidenceDefinition(
                    id="developer_broad_knowledge",
                    name="Developer Broad Knowledge",
                    category="developer",
                    description="Developer has interacted with many distinct subsystems.",
                    semantic_meaning="Developer is expanding cross-system understanding.",
                    triggering_conditions=(
                        EvidenceRule(
                            id="spread-high",
                            measurement_id="developer_knowledge_spread",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=0.8,
                            weight=1.0,
                            field_source="percentile",
                        ),
                    ),
                    required_measurements=("developer_knowledge_spread",),
                    optional_measurements=("developer_subsystem_focus",),
                    synthesis_rules=("required_measurement_present",),
                    confidence_strategy="factor_product_with_explanation",
                    validation_rules=("logical",),
                    interpretation="Developer possesses broad architectural context.",
                    standards_references=(),
                    business_interpretation="Valuable for cross-team reviews.",
                    known_limitations=(),
                    version_history=("1.0",),
                    severity=EvidenceSeverity.LOW,
                    rule_reliability=0.8,
                ),
                EvidenceDefinition(
                    id="developer_knowledge_island",
                    name="Developer Knowledge Island",
                    category="ownership",
                    description="Developer is highly concentrated in a single subsystem.",
                    semantic_meaning="Potential siloed knowledge.",
                    triggering_conditions=(
                        EvidenceRule(
                            id="focus-high",
                            measurement_id="developer_subsystem_focus",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=0.9,
                            weight=1.0,
                            field_source="percentile",
                        ),
                    ),
                    required_measurements=("developer_subsystem_focus",),
                    optional_measurements=("developer_knowledge_spread",),
                    synthesis_rules=("required_measurement_present",),
                    confidence_strategy="factor_product_with_explanation",
                    validation_rules=("logical",),
                    interpretation="Developer is a deep specialist in this area.",
                    standards_references=(),
                    business_interpretation="Key person dependency risk if bus factor is low.",
                    known_limitations=(),
                    version_history=("1.0",),
                    severity=EvidenceSeverity.MEDIUM,
                    rule_reliability=0.85,
                ),
                EvidenceDefinition(
                    id="active_developer_signal",
                    name="Active Developer Signal",
                    category="developer",
                    description="Developer has contributed very recently.",
                    semantic_meaning="Developer is currently active in the codebase.",
                    triggering_conditions=(
                        EvidenceRule(
                            id="recency-high",
                            measurement_id="developer_recency_score",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=0.5,
                            weight=1.0,
                        ),
                    ),
                    required_measurements=("developer_recency_score",),
                    optional_measurements=(),
                    synthesis_rules=("required_measurement_present",),
                    confidence_strategy="factor_product_with_explanation",
                    validation_rules=("logical",),
                    interpretation="Safe to assign reviews or tasks to this developer.",
                    standards_references=(),
                    business_interpretation="Active engineering resource.",
                    known_limitations=(),
                    version_history=("1.0",),
                    severity=EvidenceSeverity.LOW,
                    rule_reliability=0.95,
                ),

                # -----------------------------------------------------------------
                # Subsystem & Architecture
                # -----------------------------------------------------------------
                EvidenceDefinition(
                    id="subsystem_instability",
                    name="Subsystem Instability",
                    category="architecture",
                    description="Subsystem is undergoing significant, highly volatile changes.",
                    semantic_meaning="Area is under heavy rework or feature development.",
                    triggering_conditions=(
                        EvidenceRule(
                            id="churn-rate-high",
                            measurement_id="subsystem_churn_rate",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=2.0,
                            weight=1.0,
                            field_source="robust_z",
                        ),
                    ),
                    required_measurements=("subsystem_churn_rate",),
                    optional_measurements=("subsystem_volatility",),
                    synthesis_rules=("required_measurement_present",),
                    confidence_strategy="factor_product_with_explanation",
                    validation_rules=("logical",),
                    interpretation="Subsystem is highly volatile.",
                    standards_references=(),
                    business_interpretation="May need stabilization before release.",
                    known_limitations=(),
                    version_history=("1.0",),
                    severity=EvidenceSeverity.MEDIUM,
                    rule_reliability=0.85,
                ),
                EvidenceDefinition(
                    id="subsystem_contributor_risk",
                    name="Subsystem Contributor Risk",
                    category="ownership",
                    description="Subsystem has a low number of unique contributors.",
                    semantic_meaning="Subsystem lacks diverse knowledge distribution.",
                    triggering_conditions=(
                        EvidenceRule(
                            id="contributors-low",
                            measurement_id="subsystem_contributor_count",
                            operator=EvidenceRuleOperator.LTE,
                            threshold=0.25,
                            weight=1.0,
                            field_source="percentile",
                        ),
                    ),
                    required_measurements=("subsystem_contributor_count",),
                    optional_measurements=("subsystem_file_concentration", "subsystem_coupling_score"),
                    synthesis_rules=("required_measurement_present",),
                    confidence_strategy="factor_product_with_explanation",
                    validation_rules=("logical",),
                    interpretation="Subsystem is maintained by a single person.",
                    standards_references=(),
                    business_interpretation="High bus factor risk.",
                    known_limitations=(),
                    version_history=("1.0",),
                    severity=EvidenceSeverity.HIGH,
                    rule_reliability=0.9,
                ),

                # -----------------------------------------------------------------
                # Ownership
                # -----------------------------------------------------------------
                EvidenceDefinition(
                    id="knowledge_concentration_risk",
                    name="Knowledge Concentration Risk",
                    category="ownership",
                    description="File is overwhelmingly owned by a single author.",
                    semantic_meaning="Single point of failure for file knowledge.",
                    triggering_conditions=(
                        EvidenceRule(
                            id="ownership-score-high",
                            measurement_id="file_ownership_score",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=0.9,
                            weight=1.0,
                            field_source="percentile",
                        ),
                    ),
                    required_measurements=("file_ownership_score",),
                    optional_measurements=("developer_files_owned",),
                    synthesis_rules=("required_measurement_present",),
                    confidence_strategy="factor_product_with_explanation",
                    validation_rules=("logical",),
                    interpretation="File changes depend on a single expert.",
                    standards_references=(),
                    business_interpretation="Cross-training required.",
                    known_limitations=(),
                    version_history=("1.0",),
                    severity=EvidenceSeverity.MEDIUM,
                    rule_reliability=0.9,
                ),

                # -----------------------------------------------------------------
                # Quality & Coverage
                # -----------------------------------------------------------------
                EvidenceDefinition(
                    id="test_coverage_signal",
                    name="Test Coverage Signal",
                    category="testing",
                    description="Test files are being actively modified.",
                    semantic_meaning="Testing practices are being applied to the area.",
                    triggering_conditions=(
                        EvidenceRule(
                            id="is-test",
                            measurement_id="file_is_test",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=1.0,
                            weight=1.0,
                        ),
                    ),
                    required_measurements=("file_is_test",),
                    optional_measurements=("file_touch_count",),
                    synthesis_rules=("required_measurement_present",),
                    confidence_strategy="factor_product_with_explanation",
                    validation_rules=("logical",),
                    interpretation="Area has automated test coverage updates.",
                    standards_references=(),
                    business_interpretation="Quality assurance activities present.",
                    known_limitations=(),
                    version_history=("1.0",),
                    severity=EvidenceSeverity.LOW,
                    rule_reliability=1.0,
                ),
                EvidenceDefinition(
                    id="documentation_coverage_signal",
                    name="Documentation Coverage Signal",
                    category="documentation",
                    description="Documentation files are being actively modified.",
                    semantic_meaning="Knowledge is being codified.",
                    triggering_conditions=(
                        EvidenceRule(
                            id="is-doc",
                            measurement_id="file_is_documentation",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=1.0,
                            weight=1.0,
                        ),
                    ),
                    required_measurements=("file_is_documentation",),
                    optional_measurements=("file_touch_count",),
                    synthesis_rules=("required_measurement_present",),
                    confidence_strategy="factor_product_with_explanation",
                    validation_rules=("logical",),
                    interpretation="Area is documented.",
                    standards_references=(),
                    business_interpretation="Knowledge transfer enablement.",
                    known_limitations=(),
                    version_history=("1.0",),
                    severity=EvidenceSeverity.LOW,
                    rule_reliability=1.0,
                ),
            )
        )

    def register(
        self,
        definition: EvidenceDefinition,
    ) -> None:
        self._definitions[definition.id] = definition

    def get(
        self,
        definition_id: str,
    ) -> EvidenceDefinition:
        return self._definitions[definition_id]

    def all(
        self,
    ) -> tuple[EvidenceDefinition, ...]:
        return tuple(self._definitions.values())
