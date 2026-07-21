# Milestone 17 - Organizational Health Index

**Status:** Completed

## Objective

Combine multiple organizational intelligence signals into a unified health score.

The system should answer:

* How healthy is a module?
* Which modules require attention?
* Which modules are organizationally resilient?
* Which modules are critical risks?

---

## Architecture

GitHub

↓

Events

↓

Evidence

↓

Expertise

↓

Ownership

↓

Risk

↓

Knowledge Risk

↓

Successor Planning

↓

Organizational Graph

↓

Team Expertise Mapping

↓

Coverage Analysis

↓

Concentration Analysis

↓

Knowledge Transfer Planning

↓

Organizational Health Index

---

## Implemented Components

### HealthReport

Represents the overall organizational health of a module.

Fields:

* module_ref
* health_score
* health_level
* coverage_score
* concentration_score
* bus_factor

---

### HealthPolicy

Strategy abstraction for health evaluation.

Responsibilities:

* Combine intelligence signals
* Produce health assessments
* Support alternative health models

---

### OrganizationalHealthPolicy

First health scoring implementation.

Inputs:

* Coverage Analysis
* Concentration Analysis
* Bus Factor Analysis

Formula:

Health Score =

0.4 × Coverage

*

0.4 × Concentration Health

*

0.2 × Bus Factor Health

Where:

Concentration Health =

(1 - concentration_score) × 100

---

### Health Levels

HEALTHY ≥ 75

WARNING ≥ 50

CRITICAL < 50

---

### HealthRisk

Represents ranked organizational health.

Fields:

* report
* rank

---

### HealthService

Coordinates health evaluation.

Responsibilities:

* Analyze health
* Rank modules
* Produce health leaderboards

---

## Validation

### Healthy Module

auth.py

Coverage = 80

Concentration = 0.30

Bus Factor = 4

Health Score = 80

Health Level = HEALTHY

---

### Critical Module

payments.py

Coverage = 10

Concentration = 0.98

Bus Factor = 1

Health Score = 9.8

Health Level = CRITICAL

---

### Ranking

Rank #1

auth.py

Health Score: 80

HEALTHY

---

Rank #2

payments.py

Health Score: 9.8

CRITICAL

---

## Outcome

PIA can now:

* Produce unified health scores
* Rank repository health
* Identify critical modules
* Summarize organizational resilience

---

## Architectural Outcome

Signals

↓

Insights

↓

Actions

↓

Health

PIA now exposes a single organizational metric built from multiple intelligence layers.

---

## Limitations

Current weights are heuristic:

Coverage Weight = 40%

Concentration Weight = 40%

Bus Factor Weight = 20%

Future versions may learn weights from historical repository outcomes.

---

## Next Milestone

### Milestone 18 - Historical Intelligence

Track organizational health, risk, ownership, and expertise over time.
