# Milestone 9 - Bus Factor Analysis

Status: Completed

## Objective

Introduce organizational risk analysis based on ownership distributions.

The system should answer:

How many people must disappear before a module becomes endangered?

---

## Architecture

GitHub

↓

Event

↓

Evidence

↓

Time-Aware Expertise

↓

Ownership

↓

Risk

---

## Implemented Components

### BusFactor

Represents organizational risk for a module.

Fields:

* module_ref
* value
* coverage
* risk_level

---

### RiskLevel

Introduced risk classification.

Values:

* HIGH
* MEDIUM
* LOW

Rules:

* Bus Factor = 1 → HIGH
* Bus Factor = 2 → MEDIUM
* Bus Factor ≥ 3 → LOW

---

### BusFactorPolicy

Strategy abstraction for risk computation.

Responsibilities:

* Transform ownership distributions into risk assessments
* Remain independent from orchestration logic

---

### OwnershipBusFactorPolicy

First risk implementation.

Algorithm:

1. Sort owners by ownership percentage
2. Accumulate ownership coverage
3. Stop when coverage threshold is reached
4. Number of required owners = Bus Factor

Default Threshold:

80%

---

### BusFactorService

Coordinates risk analysis.

Responsibilities:

* Retrieve ownership information
* Delegate risk computation to a policy
* Return BusFactor assessments

---

## Validation

Module:

packages/react-devtools-facade/src/DevToolsFacade.js

Result:

Bus Factor:

1

Coverage:

100.00%

Risk Level:

HIGH

---

## Outcome

PIA can now infer:

* Knowledge concentration
* Ownership fragility
* Organizational risk

The system has moved beyond expertise estimation and now reasons about project resilience.

---

## Architectural Outcome

Activity

↓

Knowledge

↓

Ownership

↓

Risk

This establishes the foundation for future organizational intelligence capabilities.

---

## Next Milestone

Milestone 10 - Knowledge Risk Detection

Identify the most dangerous modules across an organization and surface actionable recommendations.
