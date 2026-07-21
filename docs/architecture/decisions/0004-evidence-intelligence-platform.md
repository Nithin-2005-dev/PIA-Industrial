# ADR 0004: Evidence Intelligence Platform

## Status

Accepted

## Context

The Measurement Operating System produces validated, confidence-scored,
uncertainty-aware facts. Previous architecture descriptions allowed expertise
or estimator components to consume evidence-like interpretations directly from
events or to reason near measurements. That boundary was too loose for a
production evidence system.

## Decision

Introduce the Evidence Intelligence Platform as the exclusive bridge between
Measurement and Expertise.

The canonical architecture is:

```text
Software Events
  -> Vendor Adapter
  -> Observation Layer
  -> Measurement Operating System
  -> Evidence Intelligence Platform
  -> Expertise Layer
  -> Reasoning Layer
  -> Decision Layer
```

The Evidence layer consumes only validated measurements, synthesizes immutable
evidence, validates it, ranks it, explains it, and exposes evidence packages to
Expertise.

Expertise must never directly consume measurements.

ADR 0005 refines the upstream boundary: Measurement consumes canonical
`Observation` objects, not legacy events or vendor payloads.

## Consequences

- Measurement responsibilities remain unchanged.
- Evidence definitions become versioned, ontology-aware, and plugin
  extensible.
- Evidence confidence must be mathematically explainable.
- Invalid evidence is blocked before Expertise.
- Legacy `app.domain.evidence.Evidence` remains for backward compatibility, but
  production Measurement-to-Expertise flow uses `app.evidence.domain.Evidence`.
