# M31 — Observation Layer

# 04_Implementation.md

---

# Implementation

## Introduction

M31 represents the first architectural milestone that modifies the internal representation of engineering events without changing the external behavior of the intelligence engine.

Unlike previous milestones, M31 does not introduce new inference algorithms or mathematical models. Instead, it establishes the infrastructure required for future probabilistic reasoning by preserving substantially more engineering information than previous versions of the system.

The implementation was intentionally designed to satisfy three constraints:

1. Preserve existing functionality.
2. Increase observable information.
3. Avoid architectural disruption.

---

# Design Goals

The implementation of M31 was guided by five primary objectives.

## Goal 1 — Preserve Engineering Facts

The adapter should preserve observable engineering information rather than compressing it into heuristic metrics.

---

## Goal 2 — Maintain Backward Compatibility

Every existing consumer of the Event model must continue functioning without modification.

This requirement prevented changes to downstream evidence extraction, expertise projection, ownership analysis, and organizational metrics.

---

## Goal 3 — Keep Events Immutable

The Event domain object already represented an immutable engineering fact.

This property was preserved.

No changes were made to:

* Event
* EntityRef
* EventType

Only the payload produced by the GitHub adapter evolved.

---

## Goal 4 — Prepare Future Mathematics

Future milestones require access to richer engineering observations.

M31 therefore prepares the architecture for:

* deterministic measurements
* probabilistic evidence
* Bayesian inference
* information-theoretic reasoning
* semantic analysis

without introducing those capabilities prematurely.

---

## Goal 5 — Minimize Risk

The implementation modifies only the normalization stage.

Everything downstream remains unchanged.

This significantly reduces regression risk.

---

# Files Modified

Only one production file required modification.

```text
backend/app/adapters/github/adapter.py
```

The `_payload()` method was redesigned to construct the Observation Layer.

---

# Files Intentionally Left Unchanged

The following files remained unchanged.

```text
backend/app/domain/event.py
backend/app/domain/entity_ref.py
backend/app/domain/event_type.py
backend/app/extractor/*
backend/app/projection/*
backend/app/dashboard/*
```

This demonstrates that the new Observation Layer integrates without disrupting existing abstractions.

---

# Payload Evolution

## Previous Payload

Before M31 the payload contained only a compressed engineering summary.

```text
payload

├── sha
├── message
├── additions
├── deletions
└── total_changes
```

This representation was sufficient for early heuristics but discarded the majority of observable engineering information.

---

## New Payload

After M31 the payload becomes

```text
payload

├── Compatibility Layer
│
│   ├── sha
│   ├── message
│   ├── additions
│   ├── deletions
│   └── total_changes
│
└── Observation

    ├── identity
    ├── temporal
    ├── actor
    ├── artifact
    ├── behavioral
    ├── semantic
    ├── process
    ├── integrity
    ├── provenance
    └── raw
```

The compatibility layer guarantees that all existing inference modules continue to function exactly as before.

---

# Observation Categories Implemented

## Identity

Stores immutable object identifiers.

Examples

* commit SHA
* node ID
* tree SHA
* parent SHAs

---

## Temporal

Stores observed timestamps.

Examples

* author timestamp
* committer timestamp

No temporal reasoning occurs.

---

## Actor

Stores observable participants.

Examples

* author
* committer
* platform identifiers

No expertise estimation occurs.

---

## Artifact

Stores modified engineering artifacts.

Examples

* filenames
* patches
* additions
* deletions
* URLs
* blob identifiers

---

## Behavioral

Stores observable engineering actions.

Examples

* files changed
* operations
* code churn

These remain observations rather than interpretations.

---

## Semantic

Stores human-readable engineering content.

Examples

* commit messages
* patches

No semantic classification occurs.

---

## Process

Stores engineering workflow information.

Examples

* parent commits
* merge lineage

---

## Integrity

Stores authenticity information.

Examples

* commit verification
* signature metadata

No confidence estimation occurs.

---

## Provenance

Stores origin metadata.

Examples

* platform
* gateway
* adapter
* event type

---

## Raw

Stores the complete GitHub response exactly as received.

No normalization.

No compression.

---

# Architectural Decisions

## Why Event Was Not Modified

The existing Event model already satisfied the mathematical definition of an immutable engineering fact.

Changing Event would have introduced unnecessary coupling.

Instead, the payload was extended while preserving the Event abstraction.

---

## Why Observation Lives Inside Payload

Embedding the Observation Layer inside the payload provides several advantages.

* Complete backward compatibility.
* Minimal architectural disruption.
* Future migration remains possible.
* Existing interfaces remain unchanged.

---

## Why Dictionaries Were Used

Although strongly typed immutable observation objects were considered, dictionaries were selected for M31.

Reasons include

* rapid schema evolution during research
* minimal disruption
* easy serialization
* flexible experimentation

Once the Observation Space stabilizes, future versions may replace dictionaries with immutable value objects.

---

# Backward Compatibility Strategy

Backward compatibility was treated as a first-class design requirement.

Every existing payload field remains available.

Therefore existing consumers continue using

```python
event.payload["total_changes"]
```

without modification.

No downstream module required changes.

---

# Information Preservation Strategy

The implementation follows a simple rule.

Every observable engineering fact should be

* preserved,
* organized,
* reproducible,
* and immutable.

Information should never be discarded simply because it is not immediately useful.

---

# Trade-offs

The implementation intentionally accepts several temporary trade-offs.

## Increased Payload Size

Observation storage increases memory usage.

This is acceptable because preserving information is more valuable than early optimization.

---

## Duplicate Information

Some normalized values also appear inside the raw observation.

This duplication is intentional.

It guarantees reproducibility and simplifies future validation.

---

## Flexible Schema

Using dictionaries sacrifices compile-time validation.

However, this flexibility accelerates research and schema evolution.

---

# Migration Path

Future milestones build upon M31 as follows.

```text
M31

Observation

↓

M32

Measurement

↓

M33

Evidence

↓

M34+

Bayesian State Estimation
```

No future milestone should modify the Observation Layer directly.

Instead, higher layers consume preserved observations.

---

# Implementation Outcome

The implementation successfully introduced a structured Observation Layer while preserving complete compatibility with the existing intelligence engine.

No inference algorithms changed.

No downstream services required modification.

The result is a substantially richer engineering representation that forms the foundation for deterministic measurements and probabilistic reasoning developed in subsequent milestones.
