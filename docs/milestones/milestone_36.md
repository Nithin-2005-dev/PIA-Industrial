# Milestone 36: Observation Layer Refactor

M36 makes Observation the stable foundation beneath the Measurement Operating
System.

## Delivered

- Immutable canonical `Observation` domain model.
- Strongly typed canonical facts for commits, pull requests, issues, reviews,
  builds, deployments, runtime, security, tests, cloud, infrastructure,
  documentation, and AI systems.
- Vendor-independent ontology and registry.
- Validation before storage and measurement.
- Append-only observation store with replay, history, incremental reads,
  batching, and streaming offsets.
- Canonical GitHub adapter translation with no raw payload exposure through the
  observation domain model.
- Measurement contract updated to `measure_observation`.
- Deprecated event compatibility bridges for older callers.
- Architecture, layer contract, ADR, and extension docs updated.

## Verification

```text
python backend/scripts/test_observation_platform.py
```
