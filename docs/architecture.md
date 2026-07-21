# PIA Architecture

## Canonical Pipeline

The platform architecture established through M51-M53 is now completely unified. The canonical runtime dependency pipeline is:

```text
GitHub / Git / Jira / Adapters
    |
    v
 Observation Layer
    |
    v
 Measurement Layer
    |
    v
 Evidence Layer
    |
    v
 Expertise Layer
    |
    v
 Knowledge Layer
    |
    v
 Knowledge Graph Layer
    |
    v
 Temporal Intelligence Layer
    |
    v
 Predictive Forecasting Layer
    |
    v
 Organization Intelligence Layer
    |
    v
 Reasoning Layer
    |
    v
 Decision Layer
    |
    v
 Executive Intelligence
```

## Layer Responsibilities

- **Observation**: Preserves immutable, vendor-neutral canonical facts (e.g. commits, PRs, issues).
- **Measurement**: Quantifies reality with deterministic, validated, unit-aware values (e.g., SLOC, churn).
- **Evidence**: Synthesizes and validates conclusions from measurements.
- **Expertise**: Applies domain knowledge to assign confidence, scores, and developer ownership profiles.
- **Knowledge**: Synthesizes expertise profiles into high-level organizational knowledge models.
- **Knowledge Graph**: Materializes a semantic representation of the organization (developers, modules, expertise, risks) using NetworkX.
- **Temporal Intelligence**: Stores and compares graphs across time, computing historical trends (Velocity, Acceleration, Momentum, Delta) and saving immutable snapshots.
- **Predictive Forecasting**: Projects temporal trends into the future (7, 30, 90 days) using deterministic models (Linear, EMA, Kinematic) mapped via `ForecastRegistry`.
- **Organization Intelligence**: Analyzes the organization's current and projected health, including Coverage, Concentration, Bus Factor, Successor readiness, and Knowledge Risks.
- **Reasoning**: Combines analytical signals into coherent natural language analysis using autonomous agentic frameworks.
- **Decision**: Translates reasoning output into structured, prioritized organizational actions.
- **Executive**: Renders a rich summary and dashboard of the final pipeline state.

## Core Architectural Principles

### 1. Inversion of Control & Dependency Injection
The platform operates through a `ServiceCollection` and `ServiceProvider`. Legacy ad-hoc scripts have been fully replaced by `PlatformContext` and modular services instantiated through `app.bootstrap.intelligence_context`. 

### 2. Immutability
`HistoricalContext`, `TemporalSnapshot`, and all core domain objects are deeply immutable. Mutations are rejected. To change state, a new snapshot is generated.

### 3. Absolute Determinism (Forecasting)
Predictions are mathematical derivatives of the `HistoricalContext`. All non-deterministic factors (like `datetime.now()`) are removed to guarantee exact reproducibility of `ForecastContext` bounds and intervals across successive engine replays.

### 4. Semantic Provenance
Every output in the pipeline explicitly lists its origins. Evidence IDs are passed into Expertise, which pass into Knowledge. Forecasts carry strict `ForecastProvenance`, explaining the model employed, variance, and confidence scores. No "black box" decisions are permitted.

## Package Map

```text
backend/app/platform
  Canonical DI pipeline orchestration, stage bindings, and service bootstrapping

backend/app/observation
  Canonical observation platform, registry, ontology, validation and store

backend/app/measurement
  Deterministic measurement operating system

backend/app/evidence
  Production-grade evidence intelligence platform

backend/app/expertise
  Expertise derivation from evidence and historical knowledge

backend/app/knowledge
  Organizational knowledge abstraction and categorization

backend/app/graph
  Semantic Knowledge Graph generation

backend/app/temporal
  Immutable historical snapshots and trend derivations

backend/app/forecast
  Deterministic predictive engine and TimeSeries models

backend/app/org_intelligence
  Organizational health, bus factor, coverage, and risk assessments

backend/app/agent & backend/app/reasoning
  Reasoning and user-facing analysis orchestration

backend/app/decision & backend/app/executive
  Decision recommendations, planning, and dashboarding
```
