# Milestone 18 - Historical Intelligence

**Status:** Completed

## Objective

Enable PIA to reason about organizational change over time.

The system should answer:

- Is module health improving?
- Is module health declining?
- Which modules are deteriorating fastest?
- Which modules require proactive attention?

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

Coverage

↓

Concentration

↓

Knowledge Transfer

↓

Health

↓

Historical Intelligence

---

## Implemented Components

### HealthSnapshot

Represents module health at a specific point in time.

Fields:

- module_ref
- health_score
- recorded_at

---

### HealthHistory

Represents historical health observations.

Fields:

- module_ref
- snapshots

---

### TrendDirection

Classification of historical behavior.

Values:

- IMPROVING
- STABLE
- DECLINING

---

### HealthTrend

Represents a trend derived from historical health.

Fields:

- module_ref
- previous_score
- current_score
- delta
- slope
- direction

---

### TrendAnalyzer

Computes historical trends.

Inputs:

- HealthHistory

Outputs:

- HealthTrend

---

### TrendRisk

Represents ranked trend analysis.

Fields:

- trend
- rank

---

### TrendService

Coordinates trend analysis.

Responsibilities:

- Analyze histories
- Rank declining modules
- Prioritize emerging risks

---

## Trend Algorithm

### Previous Approach

Used only:

Current - Previous

Example:

81 → 80

Delta = -1

Result:

STABLE

---

### New Approach

Uses entire history.

Formula:

Slope =

(last_score - first_score)

/

(number_of_snapshots - 1)

Example:

92

88

81

80

Slope:

(80 - 92)

/

3

=

-4

Result:

DECLINING

---

## Validation

### Health Trend

Input:

92

88

81

80

Output:

First: 92

Current: 80

Delta: -12

Slope: -4

Direction: DECLINING

---

### Trend Ranking

Rank #1

payments.py

Slope: -18.33

Direction: DECLINING

---

Rank #2

auth.py

Slope: -4.00

Direction: DECLINING

---

## Outcome

PIA can now:

- Track health over time
- Detect deterioration
- Detect improvement
- Rank declining modules
- Identify emerging organizational risks

---

## Architectural Outcome

Health

↓

History

↓

Trend

PIA now reasons about change, not only state.

---

## Limitations

Current trend analysis assumes linear behavior.

Future versions may use:

- Moving averages
- Regression models
- Exponential smoothing
- Forecast confidence intervals

---

## Next Milestone

### Milestone 19 - Forecasting

Predict future organizational health from historical trends.