from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.intelligence.measurement.domain import MeasurementDefinition
from app.intelligence.measurement.domain import MeasurementUnit


class MeasurementDataType(str, Enum):
    INTEGER = "integer"
    FLOAT = "float"
    RATIO = "ratio"


@dataclass(frozen=True)
class ScientificMeasurementDefinition:
    id: str
    name: str
    description: str
    unit: MeasurementUnit
    data_type: MeasurementDataType
    provider: str
    version: str
    dependencies: tuple[str, ...] = ()
    minimum: float | None = None
    maximum: float | None = None

    def to_measurement_definition(
        self,
    ) -> MeasurementDefinition:
        return MeasurementDefinition(
            id=self.id,
            name=self.name,
            description=self.description,
            unit=self.unit,
            version=self.version,
            minimum=self.minimum,
            maximum=self.maximum,
            dependencies=self.dependencies,
            category=self.provider,
            aggregation_strategy="none",
        )


class ScientificMeasurementRegistry:
    def __init__(
        self,
        definitions: tuple[ScientificMeasurementDefinition, ...] = (),
    ):
        self._definitions: dict[str, ScientificMeasurementDefinition] = {}
        for definition in definitions:
            self.register(definition)

    def register(
        self,
        definition: ScientificMeasurementDefinition,
    ) -> None:
        self._definitions[definition.id] = definition

    def get(
        self,
        measurement_id: str,
    ) -> ScientificMeasurementDefinition:
        return self._definitions[measurement_id]

    def all(
        self,
    ) -> tuple[ScientificMeasurementDefinition, ...]:
        return tuple(self._definitions.values())


def default_scientific_measurements(
) -> tuple[ScientificMeasurementDefinition, ...]:
    return (
        ScientificMeasurementDefinition(
            id="lines_added",
            name="Lines Added",
            description="Total added lines in a code change.",
            unit=MeasurementUnit.LOC,
            data_type=MeasurementDataType.INTEGER,
            provider="structural",
            version="1.0",
            minimum=0.0,
        ),
        ScientificMeasurementDefinition(
            id="lines_deleted",
            name="Lines Deleted",
            description="Total deleted lines in a code change.",
            unit=MeasurementUnit.LOC,
            data_type=MeasurementDataType.INTEGER,
            provider="structural",
            version="1.0",
            minimum=0.0,
        ),
        ScientificMeasurementDefinition(
            id="files_modified",
            name="Files Modified",
            description="Number of modified files in an observation.",
            unit=MeasurementUnit.COUNT,
            data_type=MeasurementDataType.INTEGER,
            provider="structural",
            version="1.0",
            minimum=0.0,
        ),
        ScientificMeasurementDefinition(
            id="directories_changed",
            name="Directories Changed",
            description="Number of unique directories changed.",
            unit=MeasurementUnit.COUNT,
            data_type=MeasurementDataType.INTEGER,
            provider="structural",
            version="1.0",
            minimum=0.0,
        ),
        ScientificMeasurementDefinition(
            id="code_churn_ratio",
            name="Code Churn Ratio",
            description="Ratio of changed lines represented by additions and deletions.",
            unit=MeasurementUnit.RATIO,
            data_type=MeasurementDataType.RATIO,
            provider="static_analysis",
            version="1.0",
            minimum=0.0,
            maximum=1.0,
        ),
        ScientificMeasurementDefinition(
            id="test_file_touch_ratio",
            name="Test File Touch Ratio",
            description="Share of changed files that appear to be tests.",
            unit=MeasurementUnit.RATIO,
            data_type=MeasurementDataType.RATIO,
            provider="static_analysis",
            version="1.0",
            minimum=0.0,
            maximum=1.0,
        ),
        ScientificMeasurementDefinition(
            id="largest_file_delta",
            name="Largest File Delta",
            description="Largest per-file changed line count in the commit.",
            unit=MeasurementUnit.LOC,
            data_type=MeasurementDataType.INTEGER,
            provider="static_analysis",
            version="1.0",
            minimum=0.0,
        ),
        ScientificMeasurementDefinition(
            id="patch_complexity_score",
            name="Patch Complexity Score",
            description="Lightweight complexity score derived from changed files and branch-like patch tokens.",
            unit=MeasurementUnit.SCORE,
            data_type=MeasurementDataType.FLOAT,
            provider="static_analysis",
            version="1.0",
            minimum=0.0,
        ),
        ScientificMeasurementDefinition(
            id="review_count",
            name="Review Count",
            description="Number of review events represented by the observation.",
            unit=MeasurementUnit.COUNT,
            data_type=MeasurementDataType.INTEGER,
            provider="review",
            version="1.0",
            minimum=0.0,
        ),
        ScientificMeasurementDefinition(
            id="comment_count",
            name="Comment Count",
            description="Number of comments associated with a review or discussion.",
            unit=MeasurementUnit.COUNT,
            data_type=MeasurementDataType.INTEGER,
            provider="review",
            version="1.0",
            minimum=0.0,
        ),
        ScientificMeasurementDefinition(
            id="review_latency_seconds",
            name="Review Latency Seconds",
            description="Time between pull request creation and update/merge.",
            unit=MeasurementUnit.SECONDS,
            data_type=MeasurementDataType.FLOAT,
            provider="review",
            version="1.0",
            minimum=0.0,
        ),
        ScientificMeasurementDefinition(
            id="issue_resolution_seconds",
            name="Issue Resolution Seconds",
            description="Time between issue creation and closure.",
            unit=MeasurementUnit.SECONDS,
            data_type=MeasurementDataType.FLOAT,
            provider="repository",
            version="1.0",
            minimum=0.0,
        ),
        ScientificMeasurementDefinition(
            id="label_count",
            name="Label Count",
            description="Number of labels attached to an issue.",
            unit=MeasurementUnit.COUNT,
            data_type=MeasurementDataType.INTEGER,
            provider="repository",
            version="1.0",
            minimum=0.0,
        ),
        ScientificMeasurementDefinition(
            id="build_duration_seconds",
            name="Build Duration Seconds",
            description="Build duration in seconds.",
            unit=MeasurementUnit.SECONDS,
            data_type=MeasurementDataType.FLOAT,
            provider="engineering",
            version="1.0",
            minimum=0.0,
        ),
        ScientificMeasurementDefinition(
            id="test_failures",
            name="Test Failures",
            description="Number of failed tests.",
            unit=MeasurementUnit.COUNT,
            data_type=MeasurementDataType.INTEGER,
            provider="engineering",
            version="1.0",
            minimum=0.0,
        ),
        ScientificMeasurementDefinition(
            id="deployment_duration_seconds",
            name="Deployment Duration Seconds",
            description="Deployment duration when available.",
            unit=MeasurementUnit.SECONDS,
            data_type=MeasurementDataType.FLOAT,
            provider="engineering",
            version="1.0",
            minimum=0.0,
        ),
        ScientificMeasurementDefinition(
            id="document_path_depth",
            name="Document Path Depth",
            description="Number of path segments in a documentation artifact.",
            unit=MeasurementUnit.COUNT,
            data_type=MeasurementDataType.INTEGER,
            provider="documentation",
            version="1.0",
            minimum=0.0,
        ),
    )
