import math
from dataclasses import dataclass
from typing import Sequence

@dataclass
class EvaluationResult:
    metric_name: str
    actual: float
    predicted: float
    error: float
    absolute_error: float
    squared_error: float
    percentage_error: float


@dataclass
class AggregateEvaluation:
    metric_name: str
    mae: float
    rmse: float
    mape: float
    evaluations_count: int


class ForecastEvaluationService:
    """
    Evaluates historical predictions against current actual states.
    """

    def evaluate(
        self,
        metric_name: str,
        actuals: Sequence[float],
        predictions: Sequence[float],
    ) -> AggregateEvaluation | None:
        if not actuals or not predictions or len(actuals) != len(predictions):
            return None

        results = []
        for actual, predicted in zip(actuals, predictions):
            error = predicted - actual
            abs_err = abs(error)
            sq_err = error * error
            pct_err = (abs_err / actual) if actual != 0 else 0.0

            results.append(
                EvaluationResult(
                    metric_name=metric_name,
                    actual=actual,
                    predicted=predicted,
                    error=error,
                    absolute_error=abs_err,
                    squared_error=sq_err,
                    percentage_error=pct_err,
                )
            )

        n = len(results)
        mae = sum(r.absolute_error for r in results) / n
        rmse = math.sqrt(sum(r.squared_error for r in results) / n)
        mape = sum(r.percentage_error for r in results) / n

        return AggregateEvaluation(
            metric_name=metric_name,
            mae=mae,
            rmse=rmse,
            mape=mape,
            evaluations_count=n,
        )
