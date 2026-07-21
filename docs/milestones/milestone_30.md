# Milestone 30 — Scenario Intelligence

## Objective

Introduce a scenario intelligence layer capable of evaluating and comparing future organizational outcomes.

Prior milestones focused on:

* Current-state intelligence
* Forecasting
* Organizational risk
* Executive recommendations

M30 extends the platform into decision-support by allowing multiple future scenarios to be evaluated and ranked.

---

# M30.1 — Scenario Framework

## Goal

Create a generic scenario execution layer that can represent future outcomes independent of scenario type.

## Added

### ScenarioOutcome

Represents a future state:

```text
strategy_name
predicted_health
future_risk_score
```

### ScenarioExecutionService

Responsible for constructing scenario outcomes.

### StrategyComparisonService

Ranks scenario outcomes by predicted health.

## Result

PIA can now represent and compare arbitrary future strategies.

---

# M30.2 — Departure Scenarios

## Goal

Evaluate organizational impact when a key owner leaves a module.

## Added

### DepartureScenarioRequest

Inputs:

```text
strategy_name
module_id
departing_owner_id
```

### DepartureScenarioService

Orchestrates:

```text
OwnershipService
↓
SuccessorService
↓
ReadinessService
↓
HealthService
↓
SimulationService
```

Produces:

```text
SimulationResult
```

## Grounding

No fixture ownership.

No fixture health.

All intelligence originates from:

```text
Ownership Pipeline
Health Pipeline
Readiness Pipeline
```

## Example

```text
Alice leaves auth.py

Health Before: 68.89
Health After: 49.66

Severity: HIGH
```

---

# M30.3 — Intervention Scenarios

## Goal

Evaluate intervention strategies before execution.

## Added

### InterventionScenarioRequest

Inputs:

```text
strategy_name
module_id
horizon
```

### InterventionScenarioService

Orchestrates:

```text
Health Pipeline
↓
Future Risk Pipeline
↓
InterventionImpactService
↓
ScenarioExecutionService
```

## Logic

```text
baseline_health
+
expected_health_gain
=
predicted_health
```

## Example

```text
Immediate knowledge transfer

Predicted Health: 52
Future Risk: 70
```

## Grounding

Forecast history is required.

Scenario evaluation uses:

```text
HealthProjection
HistoryService
ForecastPipelineService
FutureRiskPipelineService
```

---

# M30.4 — Strategy Scenarios

## Goal

Compare multiple strategy types inside a unified framework.

## Added

### StrategyScenarioRequest

Inputs:

```text
module_id
departing_owner_id
horizon
```

### StrategyScenarioService

Orchestrates:

```text
DepartureScenarioService
+
InterventionScenarioService
```

and normalizes results into:

```text
ScenarioOutcome
```

for comparison.

## Result

PIA can compare:

```text
Owner Departure
vs
Do Nothing
vs
Knowledge Transfer
```

using a single ranking mechanism.

---

# Architecture

```text
                    StrategyScenarioService
                               │
          ┌────────────────────┴────────────────────┐
          │                                         │
          ▼                                         ▼

DepartureScenarioService            InterventionScenarioService
          │                                         │
          ▼                                         ▼

SimulationResult                    ScenarioOutcome
          │                                         │
          └──────────────┬──────────────────────────┘
                         ▼

              StrategyComparisonService
```

---

# Validation

## M30.2

```text
Alice leaves

Health Before: 68.89
Health After: 49.66

Severity: HIGH
```

## M30.3

```text
Immediate knowledge transfer

Predicted Health: 52.00
Future Risk: 70.00
```

## M30.4

```text
Immediate knowledge transfer
Health: 98.89

baseline
Health: 68.89

Owner Departure
Health: 49.66
```

---

# Research Notes

## Key Architectural Decision

Interventions currently affect:

```text
Health
Future Risk
```

They do NOT currently affect:

```text
Readiness
Ownership
Bus Factor
Concentration
```

Therefore M30.4 compares strategies but does not model:

```text
Knowledge transfer
↓
Improved successor readiness
↓
Reduced departure impact
```

because the current intelligence model does not support that relationship.

This was intentionally deferred to a future milestone.

---

# Deliverables

Added:

```text
app/scenario/scenario_outcome.py

app/scenario/scenario_execution_service.py

app/scenario/departure_scenario_request.py
app/scenario/departure_scenario_service.py

app/scenario/intervention_scenario_request.py
app/scenario/intervention_scenario_service.py

app/scenario/strategy_scenario_request.py
app/scenario/strategy_scenario_service.py

app/scenario/strategy_comparison_service.py
```

Added test coverage:

```text
test_departure_scenario_service.py
test_intervention_scenario_service.py
test_strategy_scenario_service.py
```

---

# Milestone Status

```text
M30.1 Scenario Framework      COMPLETE
M30.2 Departure Scenarios     COMPLETE
M30.3 Intervention Scenarios  COMPLETE
M30.4 Strategy Scenarios      COMPLETE
```

Scenario Intelligence is now operational.
