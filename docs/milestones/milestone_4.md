# Milestone 4 - Evidence to Expertise Estimation

Status: Completed

## Objective

Transform Evidence into continuously evolving Expertise Estimates.

## Architecture

GitHub

↓

Event

↓

Evidence

↓

Expertise Estimator

↓

Expertise Estimate

## Implemented Components

### EvidenceScoringPolicy

Strategy abstraction for evaluating Evidence contributions.

Supported future implementations:

- Rule Based
- Bayesian
- Machine Learning
- Graph Neural Networks
- LLM Reasoning

### RuleExpertiseScoringPolicy

Initial scoring implementation.

Examples:

- MODIFIED = 1.0
- REVIEWED = 2.0
- FIXED = 5.0

### ExpertiseEstimator

Implements latent state transitions.

Inputs:

- Current Estimate
- Evidence
- Estimation Context

Output:

- Updated Estimate

### ExpertiseProjection

Maintains expertise state for all observed:

Developer ↔ Module

relationships.

### ExpertiseEstimateFactory

Creates initial expertise states.

Baseline values:

- raw_score = 0.0
- confidence = 0.0

---

## Estimation Formula

### Score Update

base_score =
    current_score × decay_factor

contribution =
    policy_score × evidence_confidence × learning_rate

new_score =
    base_score + contribution

### Confidence Initialization & Update

Initial confidence (when evidence extracted):

confidence_baseline = 1.0

Confidence update formula:

new_confidence = 
    min(
        1.0,
        current_confidence + (evidence_confidence × 0.1)
    )

**Rationale:** Confidence increments by 0.1 for each evidence observation, capped at 1.0 representing maximum certainty.

### Learning Rate Baseline

learning_rate_baseline = 1.0

**Behavior:** Learning rate is set by EstimationContext (caller), defaulting to 1.0. It acts as a global scaling factor for all expertise updates. Can be adjusted to tune learning velocity without modifying evidence or scoring policies.

---

## Component Formulas

### Evidence Confidence Value

**Source:** ExpertiseExtractor

**Value:** 1.0 (hardcoded for all extracted evidence from commits)

**Meaning:** Direct observations from VCS commits are assumed to have perfect confidence of intent.

---

## Complete Expertise Update Example

Given:
- Current expertise: raw_score=50, confidence=0.5
- Evidence: MODIFIED predicate, 332 changes (strength=3.0), confidence=1.0
- Learning rate: 1.0
- Decay factor: 0.99 (from ExponentialDecayPolicy)

Calculation:

1. decay_base = 50 × 0.99 = 49.5
2. contribution = 1.0 (MODIFIED) × 3.0 (strength) × 1.0 (evidence confidence) × 1.0 (learning rate) = 3.0
3. new_raw_score = 49.5 + 3.0 = 52.5
4. new_confidence = min(1.0, 0.5 + (1.0 × 0.1)) = 0.6

## Validation

Successfully executed:

GitHub
↓
Event
↓
Evidence
↓
Expertise Estimate

using live facebook/react commits.

## Outcome

The system now maintains continuously evolving expertise state derived from observed developer activity.

## Next Milestone

Milestone 5 - Expertise Graph and Query Engine