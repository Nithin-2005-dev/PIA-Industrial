# Measurement Math

## Purpose

Capture formulas used or planned in measurement.

## Scope

Covers entropy, confidence, uncertainty, calibration, fusion, and composites.

## Background

Measurements must be scientifically interpretable and mathematically bounded.

## Complete Explanation

Common formulas:

```text
entropy = -sum(p_i log p_i)
weighted_composite = sum(w_i x_i) / sum(w_i)
z_score = (x - mean) / std
mad_score = (x - median) / MAD
precision = 1 / variance
fused_mean = sum(precision_i * x_i) / sum(precision_i)
```

## Mathematical Foundations

Uncertainty is represented with intervals and variance. Derived formulas should propagate uncertainty from dependencies. For simple weighted averages, variance can be approximated by weighted source variances.

## Architecture Diagram

```mermaid
flowchart LR
  Raw --> Normalized
  Normalized --> Uncertainty
  Uncertainty --> Confidence
  Confidence --> Quality
```

## Design Decisions

- Favor bounded, explainable formulas.
- Record formula and dependencies in lineage.

## Tradeoffs

Simple formulas are interpretable but may underfit complex organizational reality.

## Failure Cases

- Division by zero in normalization.
- Entropy over empty distributions.
- Overconfident fusion of correlated sources.

## Edge Cases

- Single-source fusion should not pretend source diversity.
- Constant populations have zero variance.

## Complexity Analysis

Most formulas are O(n). Pairwise disagreement can be O(n^2).

## Current Implementation Status

Entropy, composites, fusion, calibration, statistical utilities, and validation exist.

## Known Limitations

Nonlinear uncertainty propagation remains basic.

## Future Improvements

Add Bayesian calibration and correlation-aware fusion.

## Related Documents

- [../research/Mathematical_Foundations.md](../research/Mathematical_Foundations.md)

