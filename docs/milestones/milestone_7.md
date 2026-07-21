# Milestone 7 - Time-Aware Expertise

Status: Completed

## Objective

Introduce expertise aging into the expertise estimation process.

The system should recognize that expertise becomes less relevant as time passes unless reinforced by new contributions.

---

## Problem

Previous expertise estimates accumulated indefinitely.

A contribution from:

* yesterday
* one year ago
* five years ago

had equal influence.

This caused expertise estimates to become stale and detached from current project reality.

---

## Architecture

GitHub

↓

Event

↓

Evidence

↓

Weighted Evidence

↓

Time-Aware Expertise

↓

Queries

↓

Decisions

---

## Implemented Components

### DecayPolicy

Introduced a dedicated strategy abstraction for expertise aging.

File:

estimator/policies/decay_policy.py

Responsibilities:

* Define expertise decay behavior
* Remain independent from estimation orchestration

---

### ExponentialDecayPolicy

First decay implementation.

File:

estimator/policies/exponential_decay_policy.py

Behavior:

score × e^(-rate × elapsed_days)

Properties:

* Smooth decay
* Never negative
* Configurable decay rate

---

### ExpertiseEstimator Refactor

Estimator now depends on:

* EvidenceScoringPolicy
* DecayPolicy

The estimator no longer receives decay behavior through EstimationContext.

Responsibilities are now properly separated.

---

### EstimationContext Simplification

Removed:

decay_factor

Context now contains only runtime information:

* current_time
* learning_rate
* replay_mode

---

## Validation

### Decay Policy Validation

Initial Score:

100

Results:

Today      → 100.00

30 Days    → 94.18

90 Days    → 83.53

180 Days   → 69.77

365 Days   → 48.19

730 Days   → 23.22

---

### Time-Aware Expertise Validation

Scenario:

* Expertise score = 100
* Last activity = 365 days ago
* New contribution arrives

Result:

Original Score → 100.00

Updated Score → 49.19

The previous expertise decayed before the new contribution was applied.

---

## Outcome

PIA now maintains expertise estimates that evolve over time.

Recent activity naturally outweighs stale historical activity.

This improves:

* Expert ranking
* Reviewer recommendation
* Future ownership detection
* Future bus factor analysis

---

## Next Milestone

Milestone 8 - Ownership Detection

Determine current ownership relationships between developers and modules using time-aware expertise.
