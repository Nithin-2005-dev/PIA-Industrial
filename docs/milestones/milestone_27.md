# Milestone 27 — Fully Grounded Simulation

## Goal

Complete simulation grounding by removing the remaining fixture-based inputs from the simulation pipeline.

Prior to M27, simulation consumed:

* fixture HealthReport
* fixture OwnershipEstimate

while readiness was already grounded.

This created a partial disconnect between repository intelligence and departure simulation.

The objective of M27 was to connect simulation directly to:

* ownership intelligence
* health intelligence
* successor intelligence
* readiness intelligence

and eliminate the final major adapter fixtures.

---

## Architecture Before

```text
HealthReport (fixture)
OwnershipEstimate (fixture)
        ↓
ReadinessService
        ↓
SimulationService
```

Simulation results were influenced by readiness but not by actual ownership or health.

---

## M27.1 — Ground Ownership

SimulationAdapter now derives ownership from:

```text
ExpertiseProjection
        ↓
OwnershipService
        ↓
OwnershipEstimate
```

instead of constructing a fixed ownership estimate.

Primary owner selection:

```text
owners_of(module)
        ↓
primary owner
```

Developer-specific simulations now retrieve the ownership estimate associated with the requested developer.

---

## M27.2 — Ground Health

SimulationAdapter now derives health from:

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

OwnershipService
        ↓
BusFactorService
        ↓
BusFactor

Coverage
Concentration
BusFactor
        ↓
HealthService
        ↓
HealthReport
```

instead of constructing a fixed health report.

---

## M27.3 — Ground Departure Target

Simulation now supports:

```text
What happens if Alice leaves?
What happens if Bob leaves?
```

using actual ownership estimates.

When no developer is supplied:

```text
primary owner
```

becomes the default departure candidate.

---

## Validation

Dataset:

```text
auth.py

alice    95
bob       3
charlie   2
```

### Before M27

```text
Health Before: 80.00
Health After: 57.67
Knowledge Loss: 0.28
Severity: MODERATE
```

Health and ownership were fixture-derived.

### After M27

Alice:

```text
Health Before: 68.89
Health After: 49.66
Knowledge Loss: 0.28
Severity: HIGH
```

Bob:

```text
Health Before: 68.89
Health After: 52.69
Knowledge Loss: 0.24
Severity: MODERATE
```

Different developers now produce different simulation outcomes.

---

## Architecture After

```text
ExpertiseProjection
        ↓
OwnershipService
        ↓
OwnershipEstimate

CoverageService
ConcentrationService
BusFactorService
        ↓
HealthService
        ↓
HealthReport

SuccessorService
        ↓
ReadinessService
        ↓
SimulationService
```

---

## Agent Grounding Status

```text
RiskAdapter            ✅
ForecastAdapter        ✅
SuccessorAdapter       ✅
TransferAdapter        ✅
InterventionAdapter    ✅
SimulationAdapter      ✅
```

All major agent adapters are now grounded through IntelligenceContext.

---

## Result

Simulation outcomes now depend on:

* real ownership distribution
* real organizational health
* real successor readiness

instead of fixed assumptions.

M27 completes the grounding of the agent layer.
