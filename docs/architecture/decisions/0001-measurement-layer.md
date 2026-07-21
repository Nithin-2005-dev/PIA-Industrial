# ADR 0001: Introduce the Measurement Layer

## Status

Accepted

## Context

The existing architecture preserves adapter observations and then extracts
evidence. M31 established that observation, measurement, evidence and state
estimation are separate mathematical spaces.

The next required capability is a deterministic Measurement Layer that turns
raw software observations into normalized, validated and traceable
measurements without redesigning the existing evidence or reasoning layers.

## Decision

Add `app.measurement` as a self-contained layer between adapter observations
and evidence extraction.

The layer provides:

- immutable measurement domain objects
- interface-first evaluators, normalizers, validators and scorers
- default commit complexity and impact evaluators
- confidence, uncertainty and quality metadata
- formula, composite and fusion engines
- ontology, registry and standards-backed catalog
- normalization pipeline stages
- finite-difference uncertainty propagation
- probabilistic precision-weighted fusion
- lineage graph and explanation API
- temporal store, cache tiers and recomputation graph
- customer measurement DSL and benchmark engine
- measurement contracts and lifecycle gates
- enterprise accuracy pipeline before evidence
- computation DAG, execution planner and cost optimizer
- semantic measurement graph and knowledge base
- MQL, lineage queries, streaming updates and active observation requests
- metric packs and marketplace installation
- measurement compression primitives
- statistical, graph, time-series, outlier and drift utilities
- plugin registry and ML calibration boundary

No external dependency is added in this milestone.

## Rationale

The first implementation should establish contracts, traceability and
reproducibility before optimizing storage or distributed execution. Keeping the
layer dependency-free preserves current project portability and avoids coupling
the domain model to a data-processing runtime too early.

## Consequences

Positive:

- downstream evidence can consume trustworthy measurement contracts
- future adapters can add measurements without modifying core orchestration
- all measurement values become auditable and reproducible
- deterministic IDs enable incremental recomputation
- customers can define custom measurements without code changes
- lineage and explanation APIs support enterprise trust workflows
- evidence can enforce a clean contract: validated measurements only
- planner and optimizer provide a path toward distributed execution

Tradeoffs:

- high-volume batch performance is not yet optimized with Arrow or Polars
- advanced ML anomaly detection is represented by boundaries, not shipped as a
  runtime dependency
- persistent storage is modeled by interfaces/in-memory foundations first
- streaming and marketplace are in-process foundations before external brokers
  or package registries are introduced

## Follow-Up Decisions

- Choose a persistent measurement store.
- Decide when to introduce Arrow, Polars or DuckDB.
- Define cross-tool normalization specs for major metric families.
- Add OpenTelemetry instrumentation once service runtime boundaries exist.
