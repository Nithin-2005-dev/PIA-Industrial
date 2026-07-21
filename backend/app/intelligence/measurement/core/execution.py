from collections.abc import Callable
from dataclasses import dataclass

from app.intelligence.measurement.domain import Measurement
from app.intelligence.measurement.core.store import MeasurementCache


@dataclass(frozen=True)
class MeasurementComputationNode:
    id: str
    dependencies: tuple[str, ...]
    cache_key: str
    cost: float
    executor: Callable[[], Measurement]


@dataclass(frozen=True)
class MeasurementExecutionPlan:
    requested_ids: tuple[str, ...]
    ordered_nodes: tuple[MeasurementComputationNode, ...]
    cached_ids: tuple[str, ...]


class MeasurementExecutionPlanner:

    def plan(
        self,
        requested_ids: tuple[str, ...],
        nodes: list[MeasurementComputationNode],
        cache: MeasurementCache | None = None,
    ) -> MeasurementExecutionPlan:
        node_by_id = {
            node.id: node
            for node in nodes
        }
        required = set()

        def visit(
            node_id: str,
        ):
            if node_id in required:
                return

            required.add(
                node_id
            )

            node = node_by_id[
                node_id
            ]

            for dependency_id in node.dependencies:
                if dependency_id in node_by_id:
                    visit(
                        dependency_id
                    )

        for requested_id in requested_ids:
            visit(
                requested_id
            )

        ordered = []
        temporary = set()
        permanent = set()

        def topo(
            node_id: str,
        ):
            if node_id in permanent:
                return

            if node_id in temporary:
                raise ValueError(
                    "measurement computation graph contains a cycle"
                )

            temporary.add(
                node_id
            )

            node = node_by_id[
                node_id
            ]

            for dependency_id in node.dependencies:
                if dependency_id in required:
                    topo(
                        dependency_id
                    )

            temporary.remove(
                node_id
            )
            permanent.add(
                node_id
            )
            ordered.append(
                node
            )

        for requested_id in requested_ids:
            topo(
                requested_id
            )

        cached_ids = []

        if cache is not None:
            cached_ids = [
                node.id
                for node in ordered
                if cache.get(
                    node.cache_key
                )
                is not None
            ]

        return MeasurementExecutionPlan(
            requested_ids=requested_ids,
            ordered_nodes=tuple(ordered),
            cached_ids=tuple(cached_ids),
        )


class MeasurementExecutor:

    def execute(
        self,
        plan: MeasurementExecutionPlan,
        cache: MeasurementCache,
    ) -> dict[str, Measurement]:
        results = {}

        for node in plan.ordered_nodes:
            cached = cache.get(
                node.cache_key
            )

            if cached is not None:
                results[
                    node.id
                ] = cached
                continue

            measurement = node.executor()
            cache.put_hot(
                measurement
            )
            results[
                node.id
            ] = measurement

        return results


@dataclass(frozen=True)
class CandidateMeasurementPath:
    id: str
    expected_confidence: float
    expected_latency_ms: float
    expected_cost: float


class CostBasedMeasurementOptimizer:

    def choose(
        self,
        candidates: list[CandidateMeasurementPath],
        minimum_confidence: float,
        maximum_latency_ms: float,
    ) -> CandidateMeasurementPath:
        feasible = [
            candidate
            for candidate in candidates
            if candidate.expected_confidence >= minimum_confidence
            and candidate.expected_latency_ms <= maximum_latency_ms
        ]

        if not feasible:
            raise ValueError(
                "no measurement path satisfies constraints"
            )

        return sorted(
            feasible,
            key=lambda candidate: (
                candidate.expected_cost,
                candidate.expected_latency_ms,
            ),
        )[0]


