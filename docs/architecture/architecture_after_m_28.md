# PIA Architecture Snapshot After M28

This is a historical snapshot. M35 supersedes the older direct
event-to-evidence pipeline with the production Measurement -> Evidence ->
Expertise contract.

## Current Canonical Flow

```text
Software Events
    |
    v
Observation Layer
    |
    v
Measurement Operating System
    |
    v
Evidence Intelligence Platform
    |
    v
Expertise Layer
    |
    v
Reasoning Layer
    |
    v
Decision Layer
```

## M28 Capability Scope

At M28, PIA modeled expertise, ownership, health, forecasting, succession,
transfer planning, simulation, and organization-level insights from repository
activity.

The M28 intelligence services remain meaningful, but their upstream grounding
now flows through validated evidence packages rather than direct measurement or
legacy extraction paths.

## Capability Graph

```text
EvidencePackage.for_expertise()
    -> Expertise Estimates
    -> Expertise Query Service
    -> Ownership Service
    -> Coverage Service
    -> Concentration Service
    -> Bus Factor Service
    -> Health Service
    -> Forecast Service
    -> Organization Risk Service
    -> Executive Dashboard
```

## Agent Layer

```text
Question
    -> Intent Classifier
    -> Context Extractor
    -> Tool Router
    -> Grounded Adapters
```

Grounded adapters should cite evidence, expertise, reasoning outputs, or
decision artifacts according to the current layer contract.
