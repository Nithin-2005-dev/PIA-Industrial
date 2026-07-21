# Milestone 49: Decision Optimization Engine

M49 adds an explicit decision optimization layer for constrained intervention planning.

## Delivered

- Added `DecisionOptimizationEngine`.
- Added `DecisionOptimizationRequest` and `DecisionOptimizationPlan`.
- Supports budget and max-item constrained optimization over intervention impacts and costs.
- Added `DecisionPlatformModule` with `decision.optimization` and `decision.portfolio` capabilities.
- Wired the default platform runtime so agent and executive depend on decision.
- Added `backend/scripts/test_decision_optimization.py`.

## Current Scope

The optimizer runs in memory and selects the highest expected health gain under constraints.

## Known Limitations

- Exhaustive search is intended for small candidate sets.
- No uncertainty-aware or multi-objective optimization yet.
- No persistent decision audit log beyond platform audit entries.
- No dependency constraints between interventions.

## Verification

`python backend/scripts/test_decision_optimization.py`

