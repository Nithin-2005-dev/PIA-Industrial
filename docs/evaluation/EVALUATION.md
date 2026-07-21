# Evaluation Methodology

PIA Industrial intelligence engines are validated against synthetic and curated benchmarks, not real-world industrial data.

## The Golden Benchmark

Our primary validation suite (`tests/validation/test_m73_golden_benchmark.py`) explicitly isolates the deterministic intelligence engines from the LLM. 

### Golden Questions Validated:
1. **Root Cause Validation**: Can the system reliably infer "Mechanical Wear" from a series of structured vibration and heat anomalies?
2. **Counterfactual Validation**: Can the system accurately recalculate a lower risk score when a hypothetical mitigating maintenance action is injected into the graph?
3. **Compliance Validation**: Can the system correctly classify an asset as `OVERDUE` based on current time vs the last recorded inspection timestamp?

## Metrics

- **Deterministic Accuracy:** Measured by the `pytest` validation suite. The deterministic engines must return 100% mathematically correct answers on the synthetic test set.
- **LLM Groundedness (Planned):** Future evaluations will measure the Copilot's adherence to the deterministic outputs using hallucination-detection frameworks.

## Limitations

Do not conflate a passing unit test suite with real-world model accuracy. 
- The causal rules in `IndustrialReliabilityRuleProvider` are currently simple heuristic approximations (e.g., Vibration = Wear) for demonstration purposes. They are not trained on actual SCADA telemetry.
- Real-world validation requires deployment to a live historian environment.
