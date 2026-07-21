"""
Verification script for M53 Predictive Forecasting Engine.
Ensures that given identical HistoricalContext, the ForecastEngine
produces identical, deterministic results.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add backend to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.forecast.engine import ForecastEngine, ForecastRegistry
from app.forecast.factory import TimeSeriesFactory
from app.forecast.baseline_models import (
    LinearTrendModel,
    ExponentialSmoothingModel,
    MovingAverageModel,
    MomentumProjectionModel,
    ConstantBaselineModel,
)
from app.temporal.models import HistoricalContext, TemporalTrend


def build_engine() -> ForecastEngine:
    registry = ForecastRegistry()
    registry.register(LinearTrendModel())
    registry.register(MomentumProjectionModel())
    registry.register(MovingAverageModel())
    registry.register(ExponentialSmoothingModel())
    registry.register(ConstantBaselineModel())
    
    return ForecastEngine(registry=registry, factory=TimeSeriesFactory)


def create_mock_history() -> HistoricalContext:
    trend1 = TemporalTrend(
        metric_name="bus_factor",
        direction="DECLINING",
        velocity=-0.5,
        acceleration=0.1,
        momentum=-2.5,
        window_size=5,
        values=(5.0, 4.5, 4.0, 3.5, 3.0),
    )
    
    trend2 = TemporalTrend(
        metric_name="knowledge_risk",
        direction="INCREASING",
        velocity=0.2,
        acceleration=0.05,
        momentum=1.0,
        window_size=5,
        values=(0.1, 0.3, 0.5, 0.7, 0.9),
    )
    
    return HistoricalContext(
        snapshot_count=5,
        current_version=5,
        previous_snapshot=None,
        delta=None,
        trends=(trend1, trend2),
        graph_diff=None,
        expertise_evolution=(),
        knowledge_evolution=(),
        has_history=True,
    )


def test_determinism():
    print("Running M53 Forecast Determinism Verification...")
    engine = build_engine()
    history = create_mock_history()
    
    # Run 1
    fc1 = engine.build_forecast_context(history, horizons=(7, 30, 90))
    
    # Run 2
    fc2 = engine.build_forecast_context(history, horizons=(7, 30, 90))
    
    # Assert
    assert fc1 == fc2, "Forecast Engine is NOT deterministic!"
    
    print("[OK] Forecast Contexts match exactly.")
    
    for metric_name, series in fc1.metrics.items():
        print(f"\nMetric: {metric_name}")
        print(f"  Current Value: {series.current_value}")
        print(f"  Model Used: {series.provenance.model_name}")
        for point in series.predictions:
            print(f"  -> Horizon {point.horizon_days}d: {point.predicted_value:.3f} [{point.interval.lower_bound:.3f}, {point.interval.upper_bound:.3f}]")
            
    print("\n[OK] Verification Passed.")


if __name__ == "__main__":
    test_determinism()
