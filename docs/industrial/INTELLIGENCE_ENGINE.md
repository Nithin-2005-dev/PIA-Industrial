# The Deterministic Intelligence Engine

The core intellectual architecture of PIA Industrial rests on the principle that **LLMs understand language, but deterministic algorithms compute facts.**

The intelligence engine orchestrates the pipeline from raw ingestion to prioritized decision support.

## The Epistemic Progression

1. **Observation**: A raw string from a document ("P-101 vibrated at 4.2mm/s").
2. **Measurement**: A normalized data point extracted from the observation (Asset: P-101, Metric: Vibration, Value: 4.2).
3. **Evidence**: An immutable fact stored in the `ObservationStore`.
4. **Knowledge**: Evidence injected into the `KnowledgeGraph` establishing spatial/temporal context.
5. **Temporal Intelligence**: Graph traversal determining sequence (Vibration occurred *before* bearing failure).
6. **Failure Intelligence**: Pattern recognition mapping recurrent anomalies to component lifecycles.
7. **Causal Intelligence**: Algorithmic generation of root-cause hypotheses based on causal rules and temporal precedence.
8. **Counterfactual Intelligence**: Graph simulations proving what *would* have happened if an edge (maintenance event) was added.
9. **Decision Intelligence**: Multi-variable weighting (risk, cost, compliance) to output a prioritized intervention list.

## LLM Boundaries

**Where LLMs are ALLOWED:**
- Entity extraction from unstructured text (via strictly constrained JSON outputs).
- Interpreting the user's natural language queries (Copilot routing).
- Summarizing the *deterministically computed* results for human consumption.

**Where LLMs are PROHIBITED:**
- Calculating risk scores.
- Determining root causes.
- Simulating counterfactual outcomes.
- Determining compliance status.

The Intelligence Engine ensures that every analytical conclusion reached by the system can be reproduced mathematically.
