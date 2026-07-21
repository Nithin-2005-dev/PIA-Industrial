from dataclasses import dataclass


@dataclass(frozen=True)
class MeasurementDefinitionKnowledge:
    measurement_id: str
    scientific_definition: str
    business_definition: str
    formula: str | None
    dependencies: tuple[str, ...]
    required_signals: tuple[str, ...]
    units: str
    expected_range: str | None
    confidence_model: str
    uncertainty_model: str
    validation_rules: tuple[str, ...]
    normalization_strategy: str
    aggregation_strategy: str
    benchmark_strategy: str
    interpretation_guide: str
    assumptions: tuple[str, ...]
    known_limitations: tuple[str, ...]
    standards_references: tuple[str, ...]
    research_references: tuple[str, ...]
    version_history: tuple[str, ...]


class SoftwareMeasurementKnowledgeBase:

    def __init__(
        self,
    ):
        self._entries = {}

    def register(
        self,
        knowledge: MeasurementDefinitionKnowledge,
    ):
        self._entries[
            knowledge.measurement_id
        ] = knowledge

    def get(
        self,
        measurement_id: str,
    ) -> MeasurementDefinitionKnowledge | None:
        return self._entries.get(
            measurement_id
        )

    def all(
        self,
    ) -> list[MeasurementDefinitionKnowledge]:
        return list(
            self._entries.values()
        )


class DefaultSoftwareMeasurementKnowledge:

    @classmethod
    def build(
        cls,
    ) -> SoftwareMeasurementKnowledgeBase:
        base = SoftwareMeasurementKnowledgeBase()

        for entry in (
            MeasurementDefinitionKnowledge(
                measurement_id="code_churn",
                scientific_definition=(
                    "Magnitude of textual code change measured as added "
                    "plus deleted lines."
                ),
                business_definition=(
                    "How much code changed in a commit or time window."
                ),
                formula="total_additions + total_deletions",
                dependencies=(),
                required_signals=(
                    "git.total_additions",
                    "git.total_deletions",
                ),
                units="LOC",
                expected_range="[0, infinity)",
                confidence_model="source reliability x coverage",
                uncertainty_model="bounded interval from signal reliability",
                validation_rules=("non_negative", "finite", "unit"),
                normalization_strategy="identity",
                aggregation_strategy="sum",
                benchmark_strategy="repository/team/org percentile",
                interpretation_guide=(
                    "Higher churn indicates larger review and change "
                    "surface, but is not inherently negative."
                ),
                assumptions=(
                    "line counts are emitted consistently by the adapter",
                ),
                known_limitations=(
                    "generated files and formatting-only changes may inflate churn",
                ),
                standards_references=("ISO-15939", "ISO-25010"),
                research_references=(
                    "Mining Software Repositories churn studies",
                ),
                version_history=("1.0 initial deterministic definition",),
            ),
            MeasurementDefinitionKnowledge(
                measurement_id="patch_complexity_delta",
                scientific_definition=(
                    "Approximate control-flow complexity introduced or "
                    "removed by patch tokens."
                ),
                business_definition=(
                    "Whether a change makes code paths more complex."
                ),
                formula="count(control_flow_tokens_added) - count(control_flow_tokens_removed)",
                dependencies=(),
                required_signals=("static.patch",),
                units="complexity",
                expected_range="(-infinity, infinity)",
                confidence_model="source reliability x patch coverage",
                uncertainty_model="bounded interval from patch availability",
                validation_rules=("finite", "semantic_consistency"),
                normalization_strategy="identity",
                aggregation_strategy="sum",
                benchmark_strategy="repository/language percentile",
                interpretation_guide=(
                    "Positive values indicate more control-flow branches."
                ),
                assumptions=("patch text contains representative changed lines",),
                known_limitations=(
                    "token approximation is not equivalent to full AST or CFG analysis",
                ),
                standards_references=("ISO-25010", "CISQ"),
                research_references=("McCabe cyclomatic complexity",),
                version_history=("1.0 token-based deterministic approximation",),
            ),
        ):
            base.register(
                entry
            )

        return base


