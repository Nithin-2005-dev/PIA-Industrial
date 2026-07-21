# Parts 5-7: Formulas, Metrics, and Calibration

## Every Formula

### 1. Robust Scaling (Z-Score)
$$ Z_{\text{robust}} = \frac{X - \text{Median}(X)}{\text{IQR}(X)} $$
- **Derivation**: Standard normally distributed bounds.
- **Intuition**: Mean/Variance scaling breaks on power-law distributed git data. Median/IQR is impervious to massive monolithic outliers.
- **Units**: Unitless standard deviations.
- **Assumptions**: $X$ contains sufficient data points to establish a stable interquartile range.

### 2. Logistic Bounding
$$ \text{Bounded} = \frac{100}{1 + e^{-Z}} $$
- **Intuition**: Maps unbounded standard deviations to a human-readable $0 \dots 100$ scale.

### 3. Confidence-Weighted Power Mean
$$ M_p = \left( \frac{\sum (w_i \cdot c_i) \cdot x_i^p}{\sum (w_i \cdot c_i)} \right)^{1/p} $$
- **Intuition**: Aggregates component scores ($x_i$) weighted by base importance ($w_i$) and mathematical confidence ($c_i$). $p=0.3$ exerts a harsh penalty on weak links without triggering multiplicative collapse.

### 4. Forecast Coefficient of Variation Penalty
$$ C = C_{\text{base}} \cdot e^{-0.5 \cdot \frac{\sqrt{\sigma^2}}{\mu}} \cdot e^{-0.01 \cdot H} $$
- **Derivation**: Exponential decay based on standard dispersion.
- **Intuition**: Highly volatile historical traces ($\sigma^2 > \mu$) should exponentially destroy our confidence in long-term ($H$) projections.

## Every Metric

### Health
- **Interpretation**: Overall systemic risk of the organization.
- **Expected Range**: $0 \dots 100$.
- **Edge Cases**: Empty repos default to $0$.

### Coverage
- **Interpretation**: Percentage of the codebase with active maintainers.
- **Expected Range**: Dynamic (IQR scaled).
- **Failure Modes**: Large auto-generated files (e.g., `package-lock.json`) can skew volume measurements if not excluded via AST filters.

### Bus Factor
- **Interpretation**: Count of primary maintainers.
- **Expected Range**: $1 \dots \infty$.
- **Edge Cases**: In short snapshot traces (e.g., 50 commits), Bus Factor trivially defaults to $1$ because files are rarely touched twice.

### Entropy (Shannon)
- **Interpretation**: Uniformity of knowledge.
- **Expected Range**: $0 \dots \log_2(N)$.
- **Failure Modes**: Sensitive to alias duplication (e.g., `John Doe` vs `jdoe`). Requires upstream author resolution.

### HHI (Herfindahl–Hirschman Index)
- **Interpretation**: Ownership monopoly concentration.
- **Expected Range**: $1/N \dots 1.0$.

### Confidence & Uncertainty
- **Interpretation**: Epistemic bounds on mathematical predictions.
- **Expected Range**: $0.0 \dots 1.0$.

## Calibration

- **Normalization**: Handled strictly via non-parametric robust statistics (Median/IQR) because Git structural data strictly violates Gaussian normality assumptions.
- **Thresholds**: We completely avoid static thresholds (e.g., "70 commits is good"). All thresholds are relative percentiles (e.g., "Top 20% of contributors").
- **Statistical Assumptions**: We assume temporal event series are stationary over short windows, allowing ARIMA-like smoothing and linear regression.
