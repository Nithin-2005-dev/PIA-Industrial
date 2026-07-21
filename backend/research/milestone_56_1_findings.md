# Milestone 56.1 Research Findings: Scientific Engineering Intelligence

## Abstract
This document outlines the theoretical and empirical research underpinning the scientific calibration of the PIA M56 framework. The calibration transitions PIA from an ad-hoc thresholding system to a robust, mathematically grounded intelligence platform capable of statistical modeling and uncertainty propagation.

## 1. Generalized Means in Organization Health

### Theoretical Foundation
Aggregating disparate metrics (Coverage, Concentration, Bus Factor) into a single "Health" score presents a mathematical challenge known as *multicriteria aggregation*.

- **Arithmetic Mean ($p=1$)**: Masks severe localized weaknesses. A `0.0` Bus Factor can be offset by a `1.0` Coverage score, producing a seemingly acceptable health score.
- **Harmonic Mean ($p=-1$)**: Highly sensitive to bottlenecks. If any single metric approaches `0`, the entire health collapses. Empirically, this proved too aggressive for engineering health, generating panic-inducing scores when partial observability is normal.

### Our Approach: Confidence-Weighted Power Mean
We utilize the Generalized Mean (Power Mean):
$$ M_p(x) = \left( \frac{\sum w_i x_i^p}{\sum w_i} \right)^{1/p} $$
By setting $p=0.3$, the model penalizes low outliers more severely than the arithmetic mean but avoids the asymptotic collapse of the harmonic mean. We further weigh each metric by its computational confidence ($w_i = c_i \cdot \text{base\_weight}$), ensuring that highly uncertain metrics exert less drag on overall health.

## 2. Information Theory and Knowledge Distribution

### Bus Factor Limitations
The deterministic "Bus Factor" (count of primary owners) provides a hard floor for resilience but fails to capture knowledge concentration within that group.

### Enhancements
- **Shannon Entropy**: $-\sum p_i \log_2(p_i)$. Measures the uniformity of knowledge. A team of 5 equal contributors has high entropy; a team of 5 where one person does 90% of the work has low entropy.
- **Gini Coefficient**: Quantifies ownership inequality. A Gini of `0` means perfect equality; `1` means total monopoly.
- **Herfindahl–Hirschman Index (HHI)**: $\sum p_i^2$. Borrowed from economics, HHI is deterministically bounded between `1/N` and `1.0`. It provides a highly stable indicator of knowledge concentration that responds immediately to monopoly scenarios.

## 3. Robust Statistics for Coverage Normalization

### Heavy-Tailed Commits
Software engineering contributions strictly follow a Pareto (power-law) distribution. A static threshold (e.g., "70 commits = Strong") breaks when applied to massive monolithic repositories vs. microservices.

### The Robust Scaling Solution
Instead of fixed thresholds or simple z-scores (which are skewed by extreme outliers), we implemented **Robust Scaling** using the Median and Interquartile Range (IQR):
$$ Z_{\text{robust}} = \frac{X - \text{Median}}{\text{IQR}} $$
This value is mapped via a standard logistic function to `[0, 100]`. This ensures the Coverage score adapts natively to the repository's inherent volume size.

## 4. Uncertainty Propagation and Statistical Confidence

### Coefficient of Variation (CV)
Forecasting confidence must distinguish between high-variance noise and stable trends.
$$ CV = \frac{\sqrt{\sigma^2}}{\mu} $$
Confidence is computed as an exponentially decaying function of CV and horizon ($H$):
$$ C = C_{\text{base}} \cdot e^{-0.5 \cdot CV} \cdot e^{-0.01 \cdot H} $$

### Error Propagation
Health uncertainty is currently propagated via a weighted linear combination of upstream uncertainties:
$$ U_{\text{health}} = \frac{\sum w_i U_i}{\sum w_i} $$
This forms the foundational framework required by downstream AI reasoning agents (M57) to determine when to trigger further evidence retrieval or express doubt.

## 5. Threats to Validity

- **Data Cardinality Limit**: Calibrations tested on `facebook/react` (50 commits). Short temporal windows naturally enforce a Bus Factor of 1 (most files only touched once). True entropy and HHI properties only emerge over larger temporal bounds (e.g., 500+ commits).
- **Linear Propagation Assumption**: Uncertainty propagation currently assumes independent normal errors. Future iterations should evaluate multivariate covariance or utilize Monte Carlo sampling for strict bounding.
