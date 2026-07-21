# Milestone 26 — Grounded Intervention Planning

## Goal

Ground intervention planning through the intelligence graph and eliminate fixture-based intervention inputs.

Before M26, intervention recommendations were generated using handcrafted:

- CoverageReport
- ConcentrationReport
- ForecastSeverity

Although the intervention algorithms were correct, the planner was disconnected from real repository intelligence.

The objective of M26 was to connect intervention planning to:

```text
Expertise
Ownership
Coverage
Concentration
Forecasting
Future Risk
```

and produce intervention recommendations from actual intelligence signals.

---

## Architecture Before

```text
CoverageReport (fixture)
ConcentrationReport (fixture)
ForecastSeverity (fixture)
        ↓
InterventionImpactService
        ↓
InterventionPlanner
```

Recommendations were generated from assumptions rather than repository state.

---

## M26.1 — Intelligence Pipeline Audit

An audit confirmed that all required intelligence services already existed:

```text
CoverageService
ConcentrationService
ForecastSeverityService
FutureRiskPipelineService
```

The missing capability was adapter grounding.

No new intervention domain logic was required.

---

## M26.2 — Ground Coverage

InterventionAdapter now derives coverage from:

```text
ExpertiseProjection
        ↓
CoverageService
        ↓
CoverageReport
```

instead of constructing a fixture.

Example:

```text
auth.py
Coverage Score: 30.00
Coverage Level: WEAK
Experts: 3
```

---

## M26.3 — Ground Concentration

InterventionAdapter now derives concentration from:

```text
ExpertiseProjection
        ↓
ConcentrationService
        ↓
ConcentrationReport
```

instead of constructing a fixture.

Example:

```text
auth.py
Concentration Score: 0.95
Concentration Level: HIGH
```

---

## M26.4 — Ground Forecast Severity

InterventionAdapter now derives severity from:

```text
HealthProjection
        ↓
HistoryService
        ↓
ForecastPipelineService
        ↓
FutureRiskPipelineService
        ↓
ForecastSeverity
```

instead of constructing a fixture.

Example:

```text
Current Health: 40
Predicted Health: 0
Severity: EXTREME
```

---

## M26.5 — End-to-End Validation

Dataset:

```text
auth.py

alice    95
bob       3
charlie   2
```

Health history:

```text
95
80
60
40
```

Agent query:

```text
How can we improve auth.py?
```

Output:

```text
1. Immediate knowledge transfer (+30.00)
2. Reduce knowledge concentration (+19.00)

Total Expected Gain: 49.00
```

---

## Debug Verification

Coverage:

```text
Coverage Score: 30.00
Coverage Level: WEAK
Experts: 3
```

Concentration:

```text
Concentration Score: 0.95
Concentration Level: HIGH
```

Severity:

```text
Current Health: 40
Predicted Health: 0
Severity Score: 1.00
Severity Level: EXTREME
```

All planner inputs were generated from intelligence services.

---

## Architecture After

```text
ExpertiseProjection
        ↓
CoverageService
        ↓
CoverageReport

ExpertiseProjection
        ↓
ConcentrationService
        ↓
ConcentrationReport

HealthProjection
        ↓
HistoryService
        ↓
ForecastPipelineService
        ↓
FutureRiskPipelineService
        ↓
ForecastSeverity

CoverageReport
ConcentrationReport
ForecastSeverity
        ↓
InterventionImpactService
        ↓
InterventionPlanner
```

---

## Agent Grounding Status

```text
RiskAdapter            ✅
ForecastAdapter        ✅
SuccessorAdapter       ✅
TransferAdapter        ✅
InterventionAdapter    ✅
SimulationAdapter      ⚠️ Partial
```

---

## Remaining Work

SimulationAdapter still contains:

```text
HealthReport fixture
OwnershipEstimate fixture
```

These become the focus of M27.

---

## Milestone Outcome

M26 completed intervention grounding.

Intervention recommendations are now driven by:

- expertise distribution
- coverage analysis
- concentration analysis
- future risk severity

rather than fixed assumptions.

This milestone completes the planning layer of the intelligence system.