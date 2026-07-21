from dataclasses import dataclass


@dataclass(frozen=True)
class ExpectedMeasurement:
    measurement_id: str
    expected_value: float
    tolerance: float


@dataclass(frozen=True)
class MeasurementTestDataset:
    id: str
    dataset_type: str
    description: str
    signals: dict
    expected_measurements: tuple[ExpectedMeasurement, ...]


class MeasurementTestCorpus:

    def __init__(
        self,
    ):
        self._datasets = {}

    @classmethod
    def default(
        cls,
    ):
        corpus = cls()

        for dataset in (
            MeasurementTestDataset(
                id="synthetic_commit_history_small",
                dataset_type="synthetic_commit_history",
                description="Small commit history with known churn.",
                signals={
                    "total_additions": 40,
                    "total_deletions": 10,
                },
                expected_measurements=(
                    ExpectedMeasurement(
                        measurement_id="code_churn",
                        expected_value=50.0,
                        tolerance=0.0,
                    ),
                ),
            ),
            MeasurementTestDataset(
                id="synthetic_dependency_graph_cycle",
                dataset_type="synthetic_dependency_graph",
                description="Dependency graph containing one cycle.",
                signals={
                    "edges": (
                        ("a", "b"),
                        ("b", "a"),
                    ),
                },
                expected_measurements=(
                    ExpectedMeasurement(
                        measurement_id="package_cyclicity",
                        expected_value=1.0,
                        tolerance=0.0,
                    ),
                ),
            ),
            MeasurementTestDataset(
                id="synthetic_runtime_trace_latency",
                dataset_type="synthetic_runtime_trace",
                description="Runtime trace with known tail latency.",
                signals={
                    "latencies_ms": (
                        10,
                        20,
                        100,
                    ),
                },
                expected_measurements=(
                    ExpectedMeasurement(
                        measurement_id="tail_latency",
                        expected_value=100.0,
                        tolerance=0.0,
                    ),
                ),
            ),
            MeasurementTestDataset(
                id="synthetic_ci_pipeline_stability",
                dataset_type="synthetic_ci_pipeline",
                description="CI runs with known pass ratio.",
                signals={
                    "runs": (
                        True,
                        True,
                        False,
                    ),
                },
                expected_measurements=(
                    ExpectedMeasurement(
                        measurement_id="build_stability",
                        expected_value=0.67,
                        tolerance=0.01,
                    ),
                ),
            ),
        ):
            corpus.register(
                dataset
            )

        return corpus

    def register(
        self,
        dataset: MeasurementTestDataset,
    ):
        self._datasets[
            dataset.id
        ] = dataset

    def get(
        self,
        dataset_id: str,
    ) -> MeasurementTestDataset:
        return self._datasets[
            dataset_id
        ]

    def all(
        self,
    ) -> list[MeasurementTestDataset]:
        return list(
            self._datasets.values()
        )


