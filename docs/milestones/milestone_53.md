# Milestone 53: Predictive Forecasting Engine

## Objective
Establish the **Predictive Forecasting Engine** for the PIA Platform, transforming historical intelligence snapshots into scientifically grounded predictions of future organizational state.

## Architecture

The Predictive Forecasting module sits squarely in the canonical runtime pipeline, situated directly after **Temporal Intelligence** and before **Organization Intelligence**. 

### Canonical Pipeline Insertion
```text
GitHub
↓
Observation
↓
Measurement
↓
Evidence
↓
Expertise
↓
Knowledge
↓
Knowledge Graph
↓
Temporal Intelligence
↓
Forecasting  <-- [M53]
↓
Organization Intelligence
↓
Reasoning
↓
Decision
↓
Executive Intelligence
```

### Core Components
- **`ForecastContext`**: A generic dictionary mapping metric names (e.g., `bus_factor`, `knowledge_risk`) to their respective `ForecastSeries`.
- **`TimeSeriesFactory`**: Extracts data from the `HistoricalContext` (specifically `TemporalTrend` tuples) and translates them into generic `TimeSeries` sequences, ensuring the forecast engine has zero knowledge of upstream snapshot structures.
- **`ForecastRegistry`**: A dependency-injected catalog of available forecast capabilities mapping specific deterministic math models to compatible organizational metrics.
- **`ForecastEngine`**: Resolves `TimeSeries` and applies prioritized models from the `ForecastRegistry` to generate forecasts at predefined horizons (`7`, `30`, `90` days).

### Baseline Models
Five deterministic models were provided as foundational baseline predictors:
1. `LinearTrendModel` (Linear Regression)
2. `ExponentialSmoothingModel` (EMA)
3. `MovingAverageModel` (Statistical Mean)
4. `MomentumProjectionModel` (Kinematic velocity/acceleration)
5. `ConstantBaselineModel` (Fallback static state)

## Execution Constraints
- **Absolute Determinism**: The engine enforces strict reproducibility. Models compute prediction intervals mathematically based entirely on the `TimeSeries` properties. Stochastic inputs (like `datetime.datetime.now()`) were completely decoupled from output calculations.
- **Strict Provenance**: Every `ForecastSeries` carries extensive provenance tracking including `ForecastProvenance`, `ForecastConfidence`, `ForecastUncertainty`, and `ForecastExplanation`. The platform avoids "black box" forecasting entirely.

## Integration & Impact
- `Organization Intelligence` (Stage 08) was updated to consume the new `ForecastContext`.
- `Executive Dashboard` (Stage 11) now natively surfaces 30-day interval predictions with confidence scores and dynamic metrics (Velocity, Momentum, Trend direction) sourced from `HistoricalContext`.
- Legacy `app/forecasting` module was deprecated in favor of the new canonical `app/forecast` implementation.
