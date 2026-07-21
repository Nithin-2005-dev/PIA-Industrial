# Milestone 45: Static Analysis Measurement Providers

M45 expands the Scientific Measurement Engine with deterministic static-analysis measurements derived from normalized commit observations.

## Delivered

- Added `StaticAnalysisMeasurementProvider`.
- Added scientific definitions for `code_churn_ratio`, `test_file_touch_ratio`, `largest_file_delta`, and `patch_complexity_score`.
- Registered the static-analysis provider in `default_measurement_providers()`.
- Exported the provider through `app.measurement.scientific_engine`.
- Added `backend/scripts/test_static_analysis_measurements.py`.

## Current Scope

Measurements are derived from commit metadata and patch text already present in normalized observations.

## Known Limitations

- No repository checkout or AST parsing.
- Complexity is a lightweight patch-token score, not full cyclomatic complexity.
- Test file detection is path-pattern based.
- Language-specific static analyzers are not integrated yet.

## Verification

`python backend/scripts/test_static_analysis_measurements.py`

