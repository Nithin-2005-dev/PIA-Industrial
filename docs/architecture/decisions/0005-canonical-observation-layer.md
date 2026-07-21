# ADR 0005: Canonical Observation Layer

## Status

Accepted

## Context

The platform had mature Measurement and Evidence layers, but Observation still
used the legacy `Event` abstraction as the primary integration object. That
allowed vendor payload shapes and event-centric language to leak toward
Measurement.

## Decision

Observation is now the canonical platform boundary. Adapters translate vendor
payloads into immutable `Observation` objects with strongly typed canonical
facts. Measurement consumes `Observation`, not vendor payloads or events.

The legacy `Event` model remains only as a deprecated compatibility bridge.

## Consequences

- Measurement is vendor-independent.
- Raw vendor payloads do not cross the observation boundary.
- Observation validation, registry, ontology, store, and streaming are explicit.
- New vendors are added by adapter translation and registry support, not by
  Measurement changes.
- Compatibility callers can still use `measure_event`, but the method first
  translates to `Observation`.
