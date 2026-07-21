# ADR 0003: Add Scientific Measurement Validation

## Status

Accepted

## Context

M32 and M33 established the Measurement Operating System and universal signal
knowledge layer. The next risk is measurement quality: definitions must be
scientifically grounded, benchmarkable, empirically calibratable and suitable
for enterprise trust.

## Decision

Add scientific validation and catalog modules under `app.measurement`.

The milestone adds:

- `EnterpriseMeasurementCatalog`
- `MeasurementAccuracyProfile`
- `ScientificValidationEngine`
- `CatalogValidationService`
- `ConfidenceCalibrationModel`
- `MeasurementTestCorpus`
- `ScientificMeasurementApi`

No existing Measurement, Signal, Registry, Planner or Evidence APIs are
removed or replaced.

## Rationale

Measurement quality belongs inside the Measurement Layer before Evidence.
Scientific metadata, accuracy profiles and validation reports give downstream
reasoning a stronger foundation without duplicating evidence or estimator
responsibilities.

## Consequences

Positive:

- measurements have explicit accuracy profiles
- catalog definitions can be validated systematically
- confidence can be calibrated against observed reliability
- synthetic corpora support regression testing
- interpretation, benchmark, uncertainty and research metadata are queryable

Tradeoffs:

- the enterprise catalog uses domain-level formulas until dedicated evaluators
  are added
- empirical calibration requires future persisted observations
- benchmark datasets remain pluggable/in-memory foundations for now

