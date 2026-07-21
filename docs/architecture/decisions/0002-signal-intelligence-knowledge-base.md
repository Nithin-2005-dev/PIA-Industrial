# ADR 0002: Add Universal Signal Intelligence And Knowledge Base

## Status

Accepted

## Context

M32 created the Measurement Operating System. To measure arbitrary future
software signals without changing the engine, the system needs a knowledge
layer that understands signal semantics, maps signals to measurement concepts
and preserves scientific definitions and standards references.

## Decision

Add signal intelligence and knowledge-base modules under `app.measurement`.

The milestone adds:

- immutable `SignalDefinition`
- dynamic `SignalRegistry`
- extensible `SignalOntology`
- layered `SemanticSignalClassifier`
- versioned `SignalMeasurementMapping`
- `SignalToMeasurementMapper`
- `SoftwareMeasurementKnowledgeBase`
- `StandardsCatalog`
- domain measurement packs
- `BenchmarkDatasetRegistry`
- `MeasurementKnowledgeApi`

No existing M32 APIs are removed or changed.

## Rationale

Signals are lower-level than measurements. Keeping signal knowledge in the
Measurement Layer preserves the rule that Evidence consumes only validated
measurements, while allowing future adapters and plugins to register new signal
sources independently.

## Consequences

Positive:

- future signal sources can be supported without engine changes
- signal-to-measurement mappings are explainable and traceable
- standards and research references become first-class metadata
- benchmark datasets can be discovered by measurement and scope
- human review can be required for low-confidence classifications

Tradeoffs:

- classifier implementations are deterministic foundations; real embedding and
  LLM integrations remain boundaries
- knowledge entries are in-memory foundations before persistent catalogs are
  selected

## Follow-Up Decisions

- Choose persistence for signal and knowledge registries.
- Add external plugin loading for domain packs.
- Add real embedding search once a vector backend is selected.
- Add human approval workflows for low-confidence signal mappings.

