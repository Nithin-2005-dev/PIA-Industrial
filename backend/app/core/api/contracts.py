from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from typing import Any


@dataclass(frozen=True, slots=True)
class RuntimePipelineInput:
    repository: str
    branch: str = "main"
    commits: int = 100
    github_token: str | None = None
    tenant_id: str = "default"
    output_directory: Path | None = None
    since_commit: str | None = None


@dataclass(frozen=True, slots=True)
class RuntimeStageExecution:
    name: str
    module: str
    version: str
    input_contract: str
    output_contract: str
    duration: float
    metadata: dict[str, Any]
    errors: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RuntimePipelineResult:
    context: Any
    completed_stages: tuple[RuntimeStageExecution, ...]
    execution_order: tuple[str, ...]
    errors: tuple[str, ...] = ()

    @property
    def succeeded(
        self,
    ) -> bool:
        return not self.errors


class MeasurementRuntimeApi(Protocol):
    def measure_observations(
        self,
        observations,
        context=None,
    ):
        ...


class EstimationRuntimeApi(Protocol):
    def estimate(
        self,
        evidence,
        context=None,
    ):
        ...


class GraphRuntimeApi(Protocol):
    def build_graph(
        self,
        context=None,
    ):
        ...


class SimulationRuntimeApi(Protocol):
    def simulate(
        self,
        scenario,
        context=None,
    ):
        ...


class ForecastingRuntimeApi(Protocol):
    def forecast(
        self,
        history,
        context=None,
    ):
        ...


class AgentRuntimeApi(Protocol):
    def answer(
        self,
        question: str,
        context=None,
    ):
        ...


class ExecutiveRuntimeApi(Protocol):
    def summarize(
        self,
        context=None,
    ):
        ...


class StorageRuntimeApi(Protocol):
    def append(
        self,
        record,
    ) -> None:
        ...
