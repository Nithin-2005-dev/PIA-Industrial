# M24 - Temporal Organizational Intelligence

Status: In Progress

## Goal

Create the temporal intelligence layer required to ground forecasting and simulation in real organizational state.

M23 connected the agent to current-state intelligence:

Evidence
-> Expertise
-> Ownership
-> Risk
-> Health

M24 extends that pipeline into time:

Health Reports
-> Health Projection
-> Health History
-> Trend
-> Forecast

---

## Problem

Forecast and simulation components already exist, but their tests and adapters still manufacture temporal inputs by hand.

Current gap:

* Trend tests manually create HealthHistory or HealthTrend
* Forecast tests manually create HealthTrend
* ForecastAdapter still uses fixture Forecast data
* Simulation still depends on missing readiness intelligence

The first missing layer is a projection that records health reports as time-series state.

---

## M24.1 HealthProjection

Introduced:

* app/history/health_projection.py
* scripts/test_health_projection.py

HealthProjection mirrors the architectural pattern established by ExpertiseProjection.

M4 pattern:

Raw Events
-> ExpertiseProjection
-> Current Expertise State

M24.1 pattern:

Health Reports
-> HealthProjection
-> Temporal Health State

Responsibilities:

* Convert HealthReport into HealthSnapshot
* Store snapshots by module id
* Return HealthHistory for one module
* Return all HealthHistory records
* Raise a clear error when a module has no history

Validation:

HealthReport
-> HealthProjection
-> HealthHistory

The first test applies three health reports for payments.py and verifies that history_of("payments.py") returns three snapshots.

---

## M24.2 HistoryService

Introduced:

* app/history/history_service.py
* scripts/test_history_service.py

HistoryService provides the orchestration path from temporal state into trend intelligence.

Pipeline:

HealthProjection
-> HistoryService
-> TrendService
-> HealthTrend

Responsibilities:

* Pull all HealthHistory records from HealthProjection
* Generate trends from projected histories
* Rank declining modules using TrendService

Validation:

HealthReport
-> HealthProjection
-> HistoryService
-> TrendService
-> HealthTrend

The test applies the sequence 95, 80, 60, 40 for payments.py and verifies that HistoryService identifies payments.py as DECLINING.

---

## M24.3 ForecastPipelineService

Introduced:

* app/forecasting/forecast_pipeline_service.py
* scripts/test_forecast_pipeline.py

ForecastPipelineService provides the orchestration path from projected health history into forecast intelligence.

Pipeline:

HealthProjection
-> HistoryService
-> ForecastService
-> Forecast

Responsibilities:

* Pull real HealthTrend records from HistoryService
* Generate forecasts for all projected histories
* Rank forecasts using ForecastService

Validation:

HealthReport
-> HealthProjection
-> HistoryService
-> ForecastPipelineService
-> ForecastService
-> Forecast

The test applies the sequence 95, 80, 60, 40 for payments.py and verifies:

* Current health is 40
* Predicted health is clamped to 0
* Forecast risk is CRITICAL

---

## Next Milestones

## M24.4 FutureRiskPipelineService

Introduced:

* app/forecasting/future_risk_pipeline_service.py
* scripts/test_future_risk_pipeline.py

FutureRiskPipelineService provides the orchestration path from projected forecast intelligence into future risk and forecast severity.

Pipeline:

HealthProjection
-> HistoryService
-> ForecastPipelineService
-> FutureRiskService
-> ForecastSeverityService

Responsibilities:

* Generate future risks from pipeline forecasts
* Rank future risks by absolute deterioration
* Generate forecast severities from pipeline forecasts
* Rank forecast severities by relative deterioration

Validation:

HealthReport
-> HealthProjection
-> HistoryService
-> ForecastPipelineService
-> FutureRiskPipelineService
-> FutureRisk
-> ForecastSeverity

The test applies the sequence 95, 80, 60, 40 for payments.py and verifies:

* Current health is 40
* Predicted health is 0
* Risk score is 40
* Severity level is EXTREME

---

## Next Milestones

### M24.5 Forecast Adapter Grounding

Connect:

ForecastAdapter
-> FutureRiskPipelineService

Outcome:

Forecast-related agent answers can use projected temporal health instead of fixture forecasts.

### M24.6 Readiness Intelligence

Introduce a service capable of computing successor readiness.

Outcome:

Simulation can move beyond fixed readiness_score inputs.

### M24.7 Simulation Grounding

Connect SimulationAdapter to readiness and projected organizational health.

---

## Outcome

M24.1 established temporal state as a first-class projection in the intelligence engine.

M24.2 connects that temporal state to existing trend intelligence.

M24.3 connects trend intelligence to existing forecast intelligence.

M24.4 connects forecast intelligence to future risk and severity intelligence.

This keeps the architecture consistent:

Projection for evolving state.
Service for analysis.
Policy for decision rules.
