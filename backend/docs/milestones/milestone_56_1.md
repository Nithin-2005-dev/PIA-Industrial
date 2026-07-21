# Milestone 56.1 — Scientific Calibration & Enhancements

## Overview

Milestone 56.1 introduces rigorous scientific models to calibrate the deterministic engineering intelligence pipeline (M56). It transitions the platform from threshold-based heuristic scores to grounded mathematical and statistical metrics (generalized means, information theory, robust scaling, statistical variance).

## Architectural & Mathematical Changes

### 1. Confidence-Weighted Power Mean (Generalized Mean)

The simple weighted arithmetic mean previously used for Organization Health was susceptible to hiding critical bottlenecks. We explored the Harmonic Mean but found it too aggressive, causing multiplicative collapse. 

Instead, we adopted the **Confidence-Weighted Power Mean (p=0.3)**:

$$ M_p = \left( \frac{\sum w_i \cdot x_i^p}{\sum w_i} \right)^{1/p} $$

With $p = 0.3$, this metric exerts a stronger penalty than the arithmetic mean (identifying critical weak links) but avoids the total collapse of the harmonic mean ($p=-1$).

**Uncertainty Propagation**: Every upstream metric (Coverage, Concentration, Bus Factor) now computes `uncertainty` and `confidence` bounds. These are propagated linearly into a final `health_uncertainty`, crucial for downstream AI reasoning.

### 2. Robust Scaling for Coverage

Fixed thresholds (e.g., 70 commits = STRONG) fail across repositories of different sizes.
We introduced **Robust Scaling (Median / IQR)**. Expertise scores are dynamically centered around the repository's median and scaled by the Interquartile Range (IQR). A sigmoid mapping bounds the result to a `[0, 100]` domain, ensuring dynamic adaptability regardless of repository size.

### 3. Information Theory: Shannon Entropy & HHI

The Bus Factor (count of primary owners) provides a deterministic floor, but lacks nuance for distributed teams. We augmented the risk model by computing:

- **Shannon Entropy**: Measures knowledge distribution uniformity.
- **Gini Coefficient**: Measures ownership inequality.
- **Herfindahl–Hirschman Index (HHI)**: $\sum p_i^2$, an extremely stable and interpretable metric for ownership concentration.

### 4. Information Coverage (Evidence)

Evidence coverage is no longer just "explained / total". We shifted to an Information Coverage model:
$$ \text{Coverage} = \frac{\text{Explained High Risks}}{\text{Total High Risks}} \times \text{Mean(Evidence Confidence)} $$
This ensures we measure the *quality* and *relevance* of the explanation, not just the raw repository size.

### 5. Statistical Forecast Confidence

Forecast confidence now utilizes the **Coefficient of Variation (CV)**:
$$ CV = \frac{\sqrt{\text{Variance}}}{\text{Mean} + \epsilon} $$
Confidence decays exponentially based on $CV$ and the prediction horizon:
$$ \text{Confidence} = \text{Base} \cdot e^{-0.5 \cdot CV} \cdot e^{-0.01 \cdot H} $$

## Calibration Methodology

We implemented a **One-at-a-Time (OAT)** Sensitivity Analysis to ensure stability. 
Metrics were tested on the `facebook/react` benchmark (50 commit trace), preserving the structural authenticity of the data (e.g., acknowledging that short commit windows legitimately produce Bus Factors of 1).

## Before vs. After Comparisons

| Metric | Before M56.1 | After M56.1 |
|--------|-------------|-------------|
| **Health Score** | ~0.026 (Collapsed) | ~50 (Power Mean bounded) |
| **Coverage Level** | 100% WEAK (Static cap) | Dynamic (IQR Scaled) |
| **Evidence Coverage** | ~0.6% (Total repo risks) | 100% (High-risk subset + Confidence) |
| **Forecast Confidence**| Static (90-100%) | Dynamic (Decays on variance/horizon) |

## Known Limitations

- **Multivariate Uncertainty**: Currently, uncertainty is propagated linearly. Future work (M58) should incorporate Monte Carlo simulations for true nonlinear uncertainty bounds.
- **Temporal Ownership**: Ownership is still based on a single snapshot. Exponential decay over time is architecturally designed but requires historical commit processing to activate.
