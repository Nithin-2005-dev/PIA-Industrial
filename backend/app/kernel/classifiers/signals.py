from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.intelligence.measurement.domain import ExpectedRange
from app.intelligence.measurement.domain import MeasurementReference
from app.intelligence.measurement.domain import MeasurementUnit
from app.intelligence.measurement.domain.contracts import MeasurementLifecycle


class SignalDataType(Enum):
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    TIMESTAMP = "timestamp"
    OBJECT = "object"
    ARRAY = "array"


@dataclass(frozen=True)
class SignalReliability:
    source_reliability: float
    adapter_reputation: float
    freshness_half_life_days: float | None = None
    notes: str | None = None

    def score(
        self,
    ) -> float:
        return max(
            0.0,
            min(
                1.0,
                self.source_reliability
                * self.adapter_reputation,
            ),
        )


@dataclass(frozen=True)
class SignalDefinition:
    id: str
    name: str
    display_name: str
    description: str
    source_adapter: str
    source_tool: str
    data_type: SignalDataType
    unit: MeasurementUnit
    semantic_category: str
    version: str
    lifecycle: MeasurementLifecycle
    value_constraints: Mapping[str, Any] = field(default_factory=dict)
    expected_range: ExpectedRange | None = None
    tags: tuple[str, ...] = ()
    provenance: Mapping[str, Any] = field(default_factory=dict)
    reliability: SignalReliability = field(
        default_factory=lambda: SignalReliability(
            source_reliability=0.75,
            adapter_reputation=0.75,
        )
    )
    supported_measurement_packs: tuple[str, ...] = ()
    validation_rules: tuple[str, ...] = ()
    references: tuple[MeasurementReference, ...] = ()


class SignalRegistry:

    def __init__(
        self,
    ):
        self._signals: dict[
            tuple[str, str],
            SignalDefinition,
        ] = {}
        self._latest_versions: dict[str, str] = {}

    def register(
        self,
        signal: SignalDefinition,
    ):
        key = (
            signal.id,
            signal.version,
        )

        if key in self._signals:
            raise ValueError(
                "signal definition version already registered"
            )

        self._signals[key] = signal

        latest = self._latest_versions.get(
            signal.id
        )

        if latest is None or signal.version > latest:
            self._latest_versions[
                signal.id
            ] = signal.version

    def get(
        self,
        signal_id: str,
        version: str | None = None,
    ) -> SignalDefinition:
        if version is None:
            version = self._latest_versions[
                signal_id
            ]

        return self._signals[
            (
                signal_id,
                version,
            )
        ]

    def by_category(
        self,
        category: str,
    ) -> list[SignalDefinition]:
        return [
            signal
            for signal in self._signals.values()
            if signal.semantic_category == category
        ]

    def all(
        self,
    ) -> list[SignalDefinition]:
        return list(
            self._signals.values()
        )


class DefaultSignalCatalog:

    @classmethod
    def build(
        cls,
    ) -> SignalRegistry:
        registry = SignalRegistry()

        for signal in cls.definitions():
            registry.register(
                signal
            )

        return registry

    @classmethod
    def definitions(
        cls,
    ) -> list[SignalDefinition]:
        return [
            SignalDefinition(
                id="git.total_additions",
                name="total_additions",
                display_name="Total Additions",
                description="Added lines reported for a source control change.",
                source_adapter="github",
                source_tool="git",
                data_type=SignalDataType.INTEGER,
                unit=MeasurementUnit.LOC,
                semantic_category="source_control",
                version="1.0",
                lifecycle=MeasurementLifecycle.PRODUCTION,
                expected_range=ExpectedRange(
                    minimum=0.0,
                ),
                tags=("git", "churn", "lines"),
                supported_measurement_packs=(
                    "git-analytics",
                    "code-quality",
                ),
                validation_rules=("non_negative", "finite"),
            ),
            SignalDefinition(
                id="git.total_deletions",
                name="total_deletions",
                display_name="Total Deletions",
                description="Deleted lines reported for a source control change.",
                source_adapter="github",
                source_tool="git",
                data_type=SignalDataType.INTEGER,
                unit=MeasurementUnit.LOC,
                semantic_category="source_control",
                version="1.0",
                lifecycle=MeasurementLifecycle.PRODUCTION,
                expected_range=ExpectedRange(
                    minimum=0.0,
                ),
                tags=("git", "churn", "lines"),
                supported_measurement_packs=(
                    "git-analytics",
                    "code-quality",
                ),
                validation_rules=("non_negative", "finite"),
            ),
            SignalDefinition(
                id="git.files",
                name="files",
                display_name="Changed Files",
                description="Files touched by a source control change.",
                source_adapter="github",
                source_tool="git",
                data_type=SignalDataType.ARRAY,
                unit=MeasurementUnit.COUNT,
                semantic_category="source_control",
                version="1.0",
                lifecycle=MeasurementLifecycle.PRODUCTION,
                expected_range=ExpectedRange(
                    minimum=0.0,
                ),
                tags=("git", "files", "change_surface"),
                supported_measurement_packs=("git-analytics",),
                validation_rules=("array",),
            ),
            SignalDefinition(
                id="static.patch",
                name="patch",
                display_name="Patch",
                description="Text diff emitted by source or static tools.",
                source_adapter="github",
                source_tool="git",
                data_type=SignalDataType.STRING,
                unit=MeasurementUnit.CUSTOM,
                semantic_category="static_analysis",
                version="1.0",
                lifecycle=MeasurementLifecycle.PRODUCTION,
                tags=("patch", "complexity", "diff"),
                supported_measurement_packs=(
                    "architecture-intelligence",
                    "code-quality",
                ),
                validation_rules=("text",),
            ),
        ]


