# Milestone 5 - Query Layer and Weighted Evidence

Status: Completed

## Objective

Transform expertise estimates into actionable answers while improving expertise quality through weighted evidence.

## Architecture

GitHub

↓

Event

↓

Evidence

↓

Weighted Evidence

↓

Expertise Estimate

↓

Query Layer

↓

Answers

---

## Implemented Components

### Query Layer

Introduced a dedicated query layer for consuming expertise state.

Files:

* query/query_result.py
* query/expertise_query_service.py

Supported queries:

* top_experts(module_id)
* module_experts(module_id)
* developer_expertise(developer_id)

---

### QueryResult

Encapsulates ranked query results.

Contains:

* ExpertiseEstimate
* effective_score

---

### Expertise Ranking

Current ranking formula:

effective_score =
raw_score × confidence

Purpose:

* raw_score measures expertise magnitude (0 to unbounded)
* confidence measures estimate certainty (0.0 to 1.0)

Both dimensions are preserved separately.

#### Confidence Growth Pattern

Initial: confidence = 0.0 (no observations)
After 1st evidence: confidence = min(1.0, 0.0 + 0.1) = 0.1
After 2nd evidence: confidence = min(1.0, 0.1 + 0.1) = 0.2
...
After 10th evidence: confidence = min(1.0, 0.9 + 0.1) = 1.0

**Effect:** Recent estimates have lower confidence multipliers; mature estimates with consistent observations reach maximum confidence of 1.0 (capped at exactly 10 independent evidence observations).

---

### Evidence Strength Policies

Introduced strength derivation as a separate concern from extraction.

Files:

extractor/policies/

* evidence_strength_policy.py
* github_commit_strength_policy.py

---

### GitHubCommitStrengthPolicy

Maps commit size to contribution magnitude.

Current buckets:

<= 10 changes → 0.1

<= 100 changes → 1.0

<= 500 changes → 3.0

<= 1000 changes → 5.0

> 1000 changes → 10.0

---

### Weighted Evidence

Evidence now contains:

metadata["strength"]

Example:

332 changes

↓

strength = 3.0

---

### Strength-Aware Expertise Estimation

Updated expertise contribution formula:

contribution =
predicate_score
× strength
× confidence
× learning_rate

This allows larger contributions to have greater influence on expertise estimates.

#### Component Formulas

**predicate_score** (from RuleExpertiseScoringPolicy):
- MODIFIED = 1.0
- REVIEWED = 2.0
- FIXED = 5.0
- CREATED = 3.0
- MERGED = 1.0
- COMMENTED = 0.2
- TOUCHED = 0.5

**strength** (from GitHubCommitStrengthPolicy):
- ≤ 10 changes → 0.1
- ≤ 100 changes → 1.0
- ≤ 500 changes → 3.0
- ≤ 1000 changes → 5.0
- \> 1000 changes → 10.0

**confidence** (from Evidence):
- Initial value: 1.0 (set when evidence extracted from VCS)
- Updated per observation: min(1.0, previous_confidence + 0.1)
- Represents certainty in expertise estimate

**learning_rate** (from EstimationContext):
- Baseline: 1.0
- Purpose: Global scaling factor for learning velocity
- Caller-controlled: Can be adjusted per execution context

#### Full Expertise Update Formula

new_confidence = 
    min(
        1.0,
        current_confidence + (evidence_confidence × 0.1)
    )

new_raw_score = 
    (current_score × decay_factor) 
    + (predicate_score × strength × confidence × learning_rate)

---

## Design Rationale: Confidence & Learning Rate

### Why Confidence Starts at 0.0, Evidence at 1.0

**ExpertiseEstimate.confidence = 0.0 (initial)**

- Represents uncertainty in a brand new estimate before any observations
- Safe default preventing premature high ranking of unverified estimates

**Evidence.confidence = 1.0 (all extractions)**

- VCS commits are treated as certain observations of developer intent
- Perfect directness: commit signature proves developer involvement
- Avoids needing to infer uncertainty from commit metadata

Separation of concerns: estimate-level confidence (learning curve) ≠ evidence-level confidence (observation quality).

### Why Confidence Increments by 0.1

new_confidence = min(1.0, current + (evidence_confidence × 0.1))

- Increments of 0.1 with max 1.0 means **exactly 10 independent evidence observations required for full confidence**
- Empirically reasonable: ~10 commits provides substantial signal about expertise
- Conservative growth prevents overfitting to outlier observations
- Reversible via decay policy if expertise becomes stale

### Why Learning Rate Defaults to 1.0

learning_rate_baseline = 1.0

- No scaling by default: every contribution weighted equally
- Allows flexibility: callers can reduce to 0.5 for "replay mode" or experimental scenarios
- Enables A/B testing learning velocity without code changes
- Keeps policy logic independent from execution context

---

## Validation

Successfully executed:

GitHub
↓
Event
↓
Evidence
↓
Weighted Evidence
↓
Expertise Estimate
↓
Query

Validated using live facebook/react commit data.

---

## Outcome

The system can now:

* Identify experts for a module
* Rank expertise estimates
* Distinguish small and large contributions
* Produce actionable organizational intelligence

---

## Next Milestone

Milestone 6 - Reviewer Recommendation Engine
