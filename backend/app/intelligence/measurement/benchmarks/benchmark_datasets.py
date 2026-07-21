from dataclasses import dataclass
from enum import Enum


class BenchmarkScope(Enum):
    REPOSITORY = "repository"
    TEAM = "team"
    ORGANIZATION = "organization"
    PROGRAMMING_LANGUAGE = "programming_language"
    FRAMEWORK = "framework"
    REPOSITORY_SIZE = "repository_size"
    INDUSTRY = "industry"
    OPEN_SOURCE = "open_source"
    INTERNAL_ENTERPRISE = "internal_enterprise"


@dataclass(frozen=True)
class BenchmarkDataset:
    id: str
    measurement_id: str
    scope: BenchmarkScope
    values: tuple[float, ...]
    version: str
    source: str
    metadata: dict


class BenchmarkDatasetRegistry:

    def __init__(
        self,
    ):
        self._datasets = {}

    def register(
        self,
        dataset: BenchmarkDataset,
    ):
        self._datasets[
            dataset.id
        ] = dataset

    def for_measurement(
        self,
        measurement_id: str,
        scope: BenchmarkScope | None = None,
    ) -> list[BenchmarkDataset]:
        return [
            dataset
            for dataset in self._datasets.values()
            if dataset.measurement_id == measurement_id
            and (
                scope is None
                or dataset.scope == scope
            )
        ]


