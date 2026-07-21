# Counterfactual Intelligence

The Counterfactual Engine answers the question: *"What would have happened if we intervened differently?"*

## Methodology

1. **Baseline Scenario**: The engine isolates the subgraph representing the actual historical events leading to a failure.
2. **Intervention**: The engine virtually injects a hypothetical edge into the graph (e.g., adding a `MAINTENANCE_ACTION` node 10 days prior to the failure).
3. **Simulation**: The Causal Engine is re-run on this modified subgraph. If the maintenance node intersects and invalidates the causal path leading to the failure, the simulation proves the failure was preventable.
4. **Risk Comparison**: The engine outputs the delta between the baseline risk score and the simulated risk score.

## Limitations

Counterfactual outputs are *modeled scenarios*, not guaranteed alternate realities. They assume that the documented intervention would have successfully mitigated the causal precursor with 100% efficacy.
