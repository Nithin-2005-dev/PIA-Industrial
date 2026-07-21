# M31 — Observation Layer

# 03_Architecture.md

---

# Architecture

## Introduction

The primary architectural contribution of M31 is the introduction of a dedicated Observation Layer between external engineering platforms and the intelligence engine.

Prior to M31, the system transformed GitHub events directly into evidence-oriented representations. Although operationally successful, this architecture tightly coupled observation acquisition with downstream inference and permanently discarded valuable engineering information.

M31 decouples these responsibilities by introducing a distinct Observation Layer responsible solely for preserving engineering facts.

---

# Previous Architecture

The original architecture can be summarized as

```text
GitHub REST API
        │
        ▼
GitHub Adapter
        │
        ▼
Compressed Event
        │
        ▼
Evidence Extraction
        │
        ▼
Expertise Projection
        │
        ▼
Organizational Metrics
```

In this architecture, normalization and compression occurred simultaneously.

Only a limited subset of GitHub information survived.

Everything else was permanently discarded.

---

# Limitations of the Previous Architecture

The previous design suffered from several architectural limitations.

## Information Loss

Normalization discarded engineering facts before any reasoning algorithm could evaluate their usefulness.

Examples included

* parent commits
* verification information
* patch contents
* artifact metadata
* provenance
* raw observations

---

## Tight Coupling

Observation acquisition and evidence generation were coupled.

This prevented independent evolution of

* observation models
* measurement algorithms
* probabilistic inference

---

## Irreversibility

Once information had been discarded, reproducing later experiments required additional GitHub API calls.

This reduced reproducibility and complicated future research.

---

# M31 Architecture

The new architecture separates engineering observation from reasoning.

```text
                    External World

                           │
                           ▼

                 GitHub REST API

                           │
                           ▼

                  GitHub Adapter

                           │
                           ▼

                  Immutable Event

                           │
                           ▼

                 Observation Layer

                           │
                           ▼

              (Future M32)

               Measurement Layer

                           │
                           ▼

              (Future M33)

                 Evidence Layer

                           │
                           ▼

              (Future M34+)

           Bayesian State Estimation

                           │
                           ▼

            Organizational Intelligence
```

This architecture introduces explicit separation between observation and inference.

---

# Event Architecture

The Event object remains unchanged.

```text
Event

├── id
├── type
├── actor_ref
├── target_refs
├── occurred_at
├── payload
└── metadata
```

Only the payload evolves.

This design preserves complete backward compatibility with existing inference modules.

---

# Payload Architecture

The payload now consists of two logical sections.

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
└── Observation Layer

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

This design allows existing consumers to continue operating without modification while enabling future inference algorithms to consume richer observations.

---

# Layer Responsibilities

Each architectural layer has exactly one responsibility.

## External Systems

Generate engineering events.

Examples include

* GitHub
* GitLab
* Jira
* Slack
* CI/CD systems

---

## Adapter Layer

Normalize external representations into platform-independent events.

Adapters perform deterministic transformation only.

No inference occurs.

---

## Observation Layer

Preserve observable engineering facts.

Responsibilities include

* information preservation
* schema organization
* deterministic normalization
* replayability

Observation never performs inference.

---

## Measurement Layer (Future)

Compute deterministic quantities from observations.

Examples include

* code churn
* entropy
* graph statistics
* semantic embeddings
* information gain

Measurements remain deterministic.

---

## Evidence Layer (Future)

Interpret measurements.

Examples include

* evidence strength
* expertise evidence
* ownership evidence
* architectural evidence

Evidence introduces uncertainty but remains observable.

---

## Bayesian State Estimation (Future)

Estimate latent organizational variables.

Examples include

* expertise
* ownership
* organizational health
* risk
* capability

These variables cannot be directly observed.

---

# Architectural Principles

M31 follows several fundamental principles.

## Single Responsibility

Every architectural layer performs exactly one conceptual task.

---

## Information Preservation

No observable engineering fact is intentionally discarded.

---

## Deterministic Normalization

Normalization must always produce identical observations for identical external inputs.

---

## Immutable Events

Events remain immutable throughout the pipeline.

Observation extends Event without altering its semantics.

---

## Backward Compatibility

Existing inference modules continue functioning without modification.

This principle allowed M31 to be introduced without rewriting downstream components.

---

# Information Flow

The architecture now follows a hierarchical information flow.

```text
Observation

↓

Measurement

↓

Evidence

↓

Knowledge

↓

Latent Organizational State

↓

Decision Support
```

Information always moves downward.

Higher layers never modify lower layers.

---

# Benefits

The new architecture provides several advantages.

## Scalability

Additional engineering platforms can be integrated without modifying inference.

---

## Extensibility

Future mathematical models consume preserved observations rather than requiring new data collection.

---

## Reproducibility

Every inference experiment can be reproduced using stored observations.

---

## Separation of Concerns

Observation acquisition, deterministic computation, probabilistic reasoning and organizational estimation become independent architectural concerns.

---

# M31 Architectural Contribution

The principal architectural contribution of M31 is the formal separation of engineering observation from organizational inference.

This separation transforms the Event object from a compressed engineering summary into a complete engineering observation while preserving compatibility with the existing intelligence engine.

The Observation Layer therefore becomes the permanent interface between external engineering systems and every future mathematical model developed within the PIA framework.
