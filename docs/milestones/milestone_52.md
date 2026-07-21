# Milestone 52 — Temporal Intelligence Engine

## Objective

Evolve PIA from a static snapshot analyzer into a time-aware organizational intelligence platform by introducing **Temporal Intelligence** as a core runtime capability.

This milestone establishes the foundational engine to track state, deltas, and trends (velocity, acceleration, and momentum) across multiple executions, enabling future milestones like predictive forecasting (M53) and counterfactual simulation (M54) to operate on historical context.

## Implementation Principles

1. **Immutable Snapshots**: Every successful execution produces an immutable `TemporalSnapshot`.
2. **Recomputable Derived Views**: Deltas, trends, and evolution summaries are derived dynamically; snapshots remain the single source of truth.
3. **Backend-Agnostic Storage**: The `SnapshotRepository` isolates I/O from the `TemporalEngine`.
4. **Calculus of Knowledge**: Time series are analyzed using kinematic concepts:
    - **State**: The current measurement value.
    - **Delta**: Raw change from the previous snapshot.
    - **Velocity**: Rate of change (first derivative).
    - **Acceleration**: Change in velocity (second derivative).
    - **Momentum**: Velocity × Mass (where mass is the temporal window length).

## Architecture Updates

The Canonical Pipeline now explicitly includes Temporal Intelligence before Organization Intelligence:

```
GitHub Commit
      ↓
 Observation
      ↓
 Measurement
      ↓
 Evidence
      ↓
 Expertise
      ↓
 Knowledge
      ↓
 Knowledge Graph
      ↓
 Temporal Intelligence     <-- (NEW)
      ↓
 Organization Intelligence
      ↓
 Reasoning
      ↓
 Decision
      ↓
 Executive Dashboard
```

Organization Intelligence (`intelligence` module) now depends on `temporal` rather than directly on `graph`, receiving a complete `HistoricalContext` to inform its algorithms.

## Key Components

- `TemporalPlatformModule`: The canonical runtime module registering temporal capabilities.
- `SnapshotRepository`: Handles storage, retrieval, and retention (defaulting to local JSON files).
- `TemporalEngine`: Orchestrates snapshot creation, computes deltas, and performs rolling-window trend analysis.
- `HistoricalContext`: The injected context object made available to all downstream modules.
- `GraphDiffEngine`: Performs metric-level structural comparison of knowledge graphs.
