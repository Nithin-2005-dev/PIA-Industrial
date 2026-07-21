"""
===============================================================================

Stage 07d: Predictive Forecasting

===============================================================================

Generates predictions of future organizational state based on historical
snapshots and deterministic kinematic/statistical models.

===============================================================================
"""

from __future__ import annotations

from .base import PipelineStage
from ..context import PlatformContext
from ..ui import metric, section, success, warning


class ForecastingStage(PipelineStage):
    name = "Forecasting"

    def execute(
        self,
        context: PlatformContext,
    ) -> None:
        from app.forecast.engine import ForecastEngine

        # Resolve ForecastEngine
        engine = context.resolve(ForecastEngine)

        if not context.historical_context or not context.historical_context.has_history:
            warning("No historical context available. Forecasting bypassed.")
            return

        # Generate forecasts for 7, 30, and 90 days
        forecast_context = engine.build_forecast_context(
            context.historical_context, horizons=(7, 30, 90)
        )
        
        context.forecast_context = forecast_context

        # Console Output
        for metric_name, series in forecast_context.metrics.items():
            section(f"Forecast: {metric_name.replace('_', ' ').title()}")
            
            # Extract basic kinematic data for display
            hist_len = series.provenance.history_length
            current_val = series.current_value
            
            metric("Historical Window", f"{hist_len} snapshots")
            metric("Current Value", f"{current_val:.2f}")

            # For showcase display, we will show the 30-day forecast details specifically
            f30 = series.get_forecast(30)
            if f30:
                metric("Forecast Horizon", "30 Days")
                metric("Forecast", f"{f30.predicted_value:.2f}")
                metric("Prediction Interval", f"[{f30.interval.lower_bound:.2f}, {f30.interval.upper_bound:.2f}]")
                metric("Confidence", f"{series.confidence.score * 100:.1f}%")
                metric("Uncertainty (Var)", f"{series.uncertainty.variance:.4f}")
                metric("Forecast Model", f"{series.provenance.model_name} (v{series.provenance.model_version})")

        success("Forecasts generated")
