# Causal Intelligence (RCA)

The `IndustrialCausalRCA` service deterministically computes Root Cause Analysis (RCA) based on the topological structure of the Knowledge Graph.

## Methodology

1. **Evidence Gathering**: The engine queries the graph for a target failure node (e.g., Pump Failure).
2. **Temporal Precedence**: It walks backward in time across `OBSERVES` and `AFFECTS` edges to find precursor anomalies (e.g., High Vibration recorded 4 hours prior).
3. **Causal Rules**: Precursors are passed through the `IndustrialReliabilityRuleProvider`, which contains domain-specific heuristic rules mapping physics-based anomalies to causal mechanisms (e.g., Vibration + Heat -> Mechanical Wear).
4. **Hypothesis Evaluation**: The engine scores candidate root causes based on temporal proximity and rule confidence.

## Limitations

- The system does not claim that deterministic rules alone *prove* real-world physics causality. It calculates the highest probability *hypotheses* based solely on the recorded evidence in the ingested documents.
