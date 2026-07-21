# Phase 11: Core Orchestrator & Fusion Engine Wiring

## Objective
The `MeasurementEngine` (the core execution pipeline) was previously treating the `MultiSourceFusionEngine` as an orphaned system, bypassing it completely. This created a severe architectural vulnerability (The Confidence Conflict) where multiple adapters observing the same entity would emit conflicting metrics, polluting the statistical baseline.

The objective of Phase 11 was to wire the Bayesian-style confidence fusion logic directly back into the execution loop of `app/measurement/core/engine.py` without violating the temporal-window boundaries belonging to the upstream Observation Layer.

## Architectural Fixes

### 1. Structural Grouping (Identity-Level)
Instead of returning a flat list of measurements blindly appended by the active evaluators, the `MeasurementEngine` now intercepts the results prior to downstream calibration.
All emitted measurements are grouped structurally based on their collision key:
```python
collision_key = f"{measurement.definition.id}_{measurement.provenance.target_entity}"
```
This guarantees that if multiple adapters (e.g., GitHub, SonarQube, Jira) output identical metric types (like `code_complexity`) for the same target developer, they are binned together for conflict resolution.

### 2. Multi-Source Fusion Integration
If a collision bin contains only a single measurement (fast path), it is passed through unchanged.
If a collision bin contains multiple conflicting measurements, the list is dynamically routed into the `MultiSourceFusionEngine`. 
The Fusion engine relies on the `DefaultConfidenceEstimator` to apply a **confidence-weighted arithmetic mean** (or a precision-weighted Bayesian fusion), mathematically favoring the adapter that possesses higher reliability for the specific observation event.

### 3. Preservation of Layer Boundaries
The execution loop in `engine.py` was carefully modified to group strictly by **structural identity** rather than **temporal windows**. 
* The **Observation Layer** (`dedupe.py`) retains sole responsibility for Stateful Stream Processing—detecting that two external webhooks firing 5 seconds apart are actually the same event, and fusing them into a unified `Observation` with a shared correlation ID.
* The **Measurement Layer** (`engine.py`) retains its stateless, deterministic nature. It only fuses when it is handed a single `Observation` object whose facts trigger duplicate metrics from varying evaluator plugins.

## Status: VERIFIED
The `verify_fusion.py` test harness confirmed the successful integration. A collision between a `0.4` confidence metric of value `100` and a `0.9` confidence metric of value `95` yielded a single, fused measurement mathematically weighted to `96.53`.

The Measurement Layer's fusion logic is now fully operational.
