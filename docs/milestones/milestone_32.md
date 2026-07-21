# Milestone 32 - Universal Measurement Engine

## Objective

Introduce a production-grade Measurement Layer that transforms preserved
software observations into deterministic, normalized, uncertainty-aware
measurements.

## Added

```text
backend/app/measurement/domain.py
backend/app/measurement/ontology.py
backend/app/measurement/registry.py
backend/app/measurement/catalog.py
backend/app/measurement/interfaces.py
backend/app/measurement/engine.py
backend/app/measurement/normalization_pipeline.py
backend/app/measurement/normalization.py
backend/app/measurement/validation.py
backend/app/measurement/confidence.py
backend/app/measurement/quality.py
backend/app/measurement/formula.py
backend/app/measurement/composite.py
backend/app/measurement/fusion.py
backend/app/measurement/lineage.py
backend/app/measurement/store.py
backend/app/measurement/recompute.py
backend/app/measurement/dsl.py
backend/app/measurement/benchmark.py
backend/app/measurement/statistical_pipeline.py
backend/app/measurement/audit.py
backend/app/measurement/accuracy.py
backend/app/measurement/active.py
backend/app/measurement/compression.py
backend/app/measurement/contracts.py
backend/app/measurement/execution.py
backend/app/measurement/knowledge_base.py
backend/app/measurement/lineage_query.py
backend/app/measurement/mql.py
backend/app/measurement/packs.py
backend/app/measurement/semantic_graph.py
backend/app/measurement/streaming.py
backend/app/measurement/statistical.py
backend/app/measurement/graph.py
backend/app/measurement/time_series.py
backend/app/measurement/outliers.py
backend/app/measurement/drift.py
backend/app/measurement/plugins.py
backend/app/measurement/ml.py
backend/app/measurement/evaluators/complexity.py
backend/app/measurement/evaluators/impact.py
backend/scripts/test_measurement_engine.py
```

## Capabilities

- Signal normalization and unit conversion.
- Measurement ontology.
- Immutable measurement registry and version lookup.
- Standards-backed default catalog.
- Pluggable cleaning, calibration, scaling and bias correction pipeline.
- Immutable measurement records.
- Explainable confidence mathematics.
- Uncertainty propagation for derived formulas.
- Measurement quality scoring.
- Validation pipeline.
- Derived formula measurements.
- Weighted composite measurements.
- Multi-source fusion.
- Probabilistic precision-weighted fusion.
- Provenance DAG and explainability API.
- Incremental recomputation dependency graph.
- Temporal append-only measurement store.
- Measurement cache tiers.
- Measurement DSL for customer-defined metrics.
- Benchmark percentile context.
- Statistical report pipeline.
- Statistical measurements.
- Graph measurements.
- Time-series measurements.
- Outlier detection.
- Drift detection.
- Plugin extension model.
- Optional ML calibration boundary.
- Audit log records.
- Measurement contracts and lifecycle gates.
- Semantic concept graph.
- Measurement knowledge base.
- Metric packs and marketplace installation.
- Enterprise accuracy pipeline before evidence.
- Computation DAG, execution planner and cache-aware executor.
- Cost-based path optimizer.
- Measurement Query Language.
- Lineage query engine.
- Streaming measurement updates.
- Active observation requests.
- Reservoir sampling and approximate histograms.

## Evidence Contract

Evidence must consume validated Measurement objects only. Raw adapter outputs
must not flow into evidence generation.

## Default Measurements

- `code_churn`
- `files_changed`
- `patch_complexity_delta`
- `change_distribution_entropy`
- `change_surface_area`
- `review_attention_need`

## Validation

Run:

```text
cd latent-engine/backend
python scripts/test_measurement_engine.py
python -m compileall app/measurement scripts/test_measurement_engine.py
```

## Status

Measurement Operating System foundation complete.
