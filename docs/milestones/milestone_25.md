# Milestone 25 — Successor Readiness & Grounded Simulation

## Goal

Introduce successor readiness as a first-class intelligence signal and integrate it into departure simulation.

Prior to this milestone, simulation used a hardcoded readiness value (`0.60`), making successor quality irrelevant to simulation outcomes.

The objective of M25 was to:

* model successor readiness explicitly
* compute readiness from expertise and successor ranking
* expose readiness through a dedicated service
* wire readiness into the application composition root
* ground simulation using successor readiness

---

## Architecture Before

```text
Departure
    ↓
SimulationAdapter
    ↓
readiness = 0.60
    ↓
SimulationService
```

Simulation outcomes were disconnected from expertise, ownership, and successor intelligence.

---

## M25.1 — Readiness Service

Implemented:

```text
ReadinessPolicy
ExpertiseReadinessPolicy
ReadinessService
SuccessorReadiness
```

Pipeline:

```text
Expertise
    ↓
Ownership
    ↓
Successor
    ↓
Readiness
```

Readiness is computed from:

* successor rank
* expertise score
* confidence score

Output:

```text
SuccessorReadiness
```

Example:

```text
bob      0.22
charlie  0.11
```

---

## M25.2 — Composition Root Integration

Extended:

```text
IntelligenceContext
```

to construct:

```text
ReadinessService
```

using:

```text
SuccessorService
ExpertiseQueryService
ExpertiseReadinessPolicy
```

New dependency graph:

```text
Projection
    ↓
Query
    ↓
Ownership
    ↓
Successor
    ↓
Readiness
```

---

## M25.3 — Agent Integration

SimulationAdapter was updated to support:

```text
IntelligenceContext
```

and consume readiness through the real service graph.

Fallback fixture behavior was preserved for non-grounded execution.

---

## M25.4 — Grounded Simulation

Initial grounding revealed an architectural flaw.

Simulation incorrectly requested readiness for:

```text
departing developer
```

instead of:

```text
selected successor
```

Incorrect flow:

```text
Alice leaves
    ↓
Readiness(Alice)
    ↓
Simulation
```

Correct flow:

```text
Alice leaves
    ↓
SuccessorService
    ↓
Bob
    ↓
Readiness(Bob)
    ↓
Simulation
```

SimulationAdapter was updated accordingly.

---

## Validation

### Scenario

```text
auth.py

alice = 95
bob = 80
charlie = 70
```

Readiness:

```text
bob      0.28
charlie  0.17
```

Simulation:

```text
Successor: bob

Health Before: 80.00
Health After: 36.80
Knowledge Loss: 0.54
Impact: -43.20
Severity: HIGH
```

The simulation outcome now depends on successor readiness.

---

## Result

Simulation is now grounded through:

```text
Expertise
    ↓
Ownership
    ↓
Successor
    ↓
Readiness
    ↓
Simulation
```

Readiness is no longer a hardcoded constant.

Simulation outcomes now respond to changes in expertise and successor quality.

---

## Remaining Work

The following adapters still contain fixtures:

```text
SimulationAdapter
    HealthReport fixture
    OwnershipEstimate fixture

InterventionAdapter
    CoverageReport fixture
    ConcentrationReport fixture
    ForecastSeverity fixture
```

These will be addressed in future milestones.

---

## Milestone Outcome

M25 successfully introduced readiness as an intelligence domain and completed readiness-driven simulation grounding.
