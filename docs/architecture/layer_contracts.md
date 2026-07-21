# Layer Contracts

## Canonical Order

```text
Software Events -> Vendor Adapter -> Observation -> Measurement -> Evidence
-> Expertise -> Reasoning -> Decision
```

## Adapter To Observation

Producer: Vendor adapters

Consumer: Observation Layer

Payload: immutable `Observation` objects with strongly typed canonical facts.

Rules:

- Adapters authenticate, fetch, parse, translate, and preserve provenance.
- Adapters may preserve vendor-observed facts such as additions, deletions,
  changed files, states, timestamps, and identifiers.
- Adapters must not calculate churn, complexity, risk, confidence, evidence,
  priority, maintainability, or business meaning.
- Raw vendor payloads may be retained inside adapter replay/debug facilities,
  but must not be exposed through `Observation`.

## Observation To Measurement

Producer: Observation Layer

Consumer: Measurement Operating System

Payload: validated immutable `app.observation.domain.Observation`.

Rules:

- Observation validates schema, type, timestamp, duplicates, source, version,
  and required fields before Measurement.
- Measurement never consumes GitHub payloads, GitLab payloads, REST DTOs,
  vendor SDK objects, or opaque JSON dictionaries.
- Measurement may quantify canonical facts, but must not mutate observations.

## Measurement To Evidence

Producer: Measurement Operating System

Consumer: Evidence Intelligence Platform

Payload: immutable `Measurement` objects that passed the Measurement Layer
validation gate.

Rules:

- Measurement calculates quantitative facts.
- Evidence does not calculate measurements.
- Evidence may use confidence, uncertainty, quality, benchmark context,
  provenance, lineage, and metadata already attached to measurements.
- Failed or not-run measurements are rejected at Evidence intake.

## Evidence To Expertise

Producer: Evidence Intelligence Platform

Consumer: Expertise Layer

Payload: `EvidencePackage.for_expertise()`.

Rules:

- Expertise consumes only validated evidence.
- Expertise must not directly consume measurements or observations.
- Evidence packages preserve tenant id, pipeline version, audit events, and
  generation timestamp.

## Reasoning To Decision

Producer: Reasoning Layer

Consumer: Decision Layer

Payload: analyses, forecasts, scenarios, and ranked recommendations grounded in
expertise over evidence.

Rules:

- Decisions should cite reasoning outputs and evidence IDs.
- Decisions should not bypass Evidence or Expertise to reinterpret raw
  observations or measurements.
