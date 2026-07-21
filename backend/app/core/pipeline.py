from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import Callable

from app.core.common import PipelineError
from app.core.common import RetryPolicy
from app.core.common import ValidationResult


class PipelineStageKind(str, Enum):
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    AGGREGATION = "aggregation"
    BRANCH = "branch"


@dataclass(frozen=True)
class PipelineContext:
    correlation_id: str | None = None
    trace_id: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class PipelineStage:
    name: str
    kind: PipelineStageKind
    handler: Callable[[Any, PipelineContext], Any]
    condition: Callable[[Any, PipelineContext], bool] | None = None
    retry_policy: RetryPolicy = RetryPolicy()
    parallel: bool = False


@dataclass(frozen=True)
class PipelineRun:
    output: Any
    completed_stages: tuple[str, ...]
    errors: tuple[PipelineError, ...] = ()


class PipelineEngine:
    def run(
        self,
        value: Any,
        stages: list[PipelineStage],
        context: PipelineContext | None = None,
    ) -> PipelineRun:
        context = context or PipelineContext()
        current = value
        completed: list[str] = []
        errors: list[PipelineError] = []

        for stage in stages:
            if stage.condition is not None and not stage.condition(
                current,
                context,
            ):
                continue

            try:
                stage_input = current
                if stage.parallel and isinstance(current, list):
                    current = [
                        stage.retry_policy.run(
                            lambda item=item: stage.handler(
                                item,
                                context,
                            )
                        )
                        for item in current
                    ]
                else:
                    current = stage.retry_policy.run(
                        lambda: stage.handler(
                            current,
                            context,
                        )
                    )
                if isinstance(current, ValidationResult) and not current.valid:
                    raise PipelineError(
                        "Pipeline validation failed",
                        code="pipeline_validation_failed",
                        details={
                            "stage": stage.name,
                            "issues": [
                                issue.message
                                for issue in current.issues
                            ],
                        },
                    )
                if isinstance(current, ValidationResult):
                    current = stage_input
                completed.append(stage.name)
            except PipelineError as exc:
                errors.append(exc)
                break
            except Exception as exc:
                errors.append(
                    PipelineError(
                        str(exc),
                        code="pipeline_stage_failed",
                        details={
                            "stage": stage.name,
                        },
                    )
                )
                break

        return PipelineRun(
            output=current,
            completed_stages=tuple(completed),
            errors=tuple(errors),
        )
