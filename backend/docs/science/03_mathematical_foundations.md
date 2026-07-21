# Part 3: Mathematical Foundations

## Observation

### Mathematical Intuition
The repository is viewed as a temporal sequence of state transitions. The Git history naturally forms a Directed Acyclic Graph (DAG) where nodes are commits and edges point to parents.

### Definitions
- **Commit Graph $G_c$**: A DAG $G_c = (V, E)$ where $v \in V$ is a commit and $e \in E$ is the parent-child relationship.

### Assumptions
- History is immutable.
- A commit perfectly encapsulates the structural delta between two states.

## Measurement

### Mathematical Intuition
Features extracted from the physical source must be normalized into bounded numerical domains to enable statistical processing downstream.

### Normalization
- **Equation**: $M_{norm} = \sigma( \frac{x - \mu}{\text{IQR}} )$
- *Intuition*: Raw counts (like Lines of Code) follow power-law distributions. We use Robust Scaling (Median and IQR) mapped through a sigmoid to guarantee measurements stay within a stable $[0, 100]$ range.

## Evidence

### Bayesian Intuition
Evidence generation treats measurements as observed variables $P(E|M)$. The presence of a high-complexity file provides Bayesian evidence of risk.

### Confidence Propagation
- **Equation**: $C_e = \prod C_m$
- *Intuition*: Evidence confidence is bounded by the compounding confidence of the underlying measurements.

## Expertise

### Weighted Scoring
- **Equation**: $E(a, f) = \sum_{t} W(c_t) \cdot e^{-\lambda(t_{now} - t)}$
- *Intuition*: An actor $a$'s expertise on a file $f$ is the sum of all their past contributions $c_t$, decayed exponentially over time.

## Knowledge Graph

### Graph Theory
The system maintains a heterogeneous property graph $G_k = (V, E)$, where $V$ includes Actors, Files, and Latent Concepts, and edges define *Knows*, *Contains*, and *Impacts*.

### Centrality
- **Degree Centrality**: Used to identify "God objects" or "Bottleneck" engineers.

## Temporal

### Time-Series Mathematics
Given a health metric $h(t)$:
- **Velocity**: $v(t) = \frac{dh}{dt} \approx h(t) - h(t-1)$
- **Acceleration**: $a(t) = \frac{dv}{dt} \approx v(t) - v(t-1)$
- **Momentum**: $p(t) = m \cdot v(t)$ (mass is analogous to codebase size).

## Forecast

### Linear Regression
- Used for stable, long-term trends like `bus_factor`. Fit via Ordinary Least Squares (OLS).

### Exponential Smoothing (EMA)
- **Equation**: $S_t = \alpha X_t + (1 - \alpha) S_{t-1}$
- *Intuition*: More recent points hold exponentially more weight. Ideal for volatile metrics.

### Confidence Estimation
- **Coefficient of Variation**: $CV = \frac{\sqrt{\sigma^2}}{\mu}$
- **Equation**: $C = C_{base} \cdot e^{-0.5 \cdot CV} \cdot e^{-0.01 \cdot H}$
- *Intuition*: Predictions degrade as the horizon $H$ increases, especially if the historical variance (CV) is high.

## Organization Intelligence

### Confidence-Weighted Power Mean
- **Equation**: $M_p = \left( \frac{\sum w_i x_i^p}{\sum w_i} \right)^{1/p}$
- *Intuition*: With $p=0.3$, we aggregate Coverage, Concentration, and Risk. This penalizes critical bottlenecks (like a Bus Factor of 0) more severely than a simple average, but avoids the total collapse of a harmonic mean.

### Information Theory (HHI & Entropy)
- **Shannon Entropy**: $H = -\sum p_i \log_2(p_i)$. Measures knowledge uniformity.
- **Herfindahl–Hirschman Index (HHI)**: $\sum p_i^2$. Measures monopoly/concentration. Ranges from $1/N$ to $1.0$.

## Causal Intelligence

### Directed Acyclic Graphs (DAGs)
Organizational risks are connected to physical files via a causal inference DAG. 
- **Root Cause Analysis**: Computed by traversing the graph backward from a systemic risk to the highest-weight edge.

## Cognitive

### Retrieval
- **Equation**: $\text{Cosine}(A, B) = \frac{A \cdot B}{||A|| ||B||}$
- *Intuition*: Used internally for semantic lookup across evidence nodes to construct highly relevant prompts for the Reasoning Orchestrator.
