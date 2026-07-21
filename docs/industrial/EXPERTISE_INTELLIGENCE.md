# Expertise Intelligence

The `ExpertiseIntelligenceService` calculates organizational risk by mapping critical knowledge concentration to specific human operators.

## Methodology

Expertise is inferred from operational evidence, not merely job titles.

1. **Evidence Gathering**: The engine queries the graph for all `PERFORMED` and `OBSERVES` edges connected to a specific asset or failure mode.
2. **Knowledge Concentration**: It calculates the distribution of interventions across operators.
3. **Bus Factor Risk**: If 90% of all successful maintenance interventions on Pump P-101 over the last two years were performed by a single engineer, the system flags a high **Critical Knowledge Concentration** risk.

## Explainability

When the Copilot recommends consulting an expert, it cites the exact historical work orders that justify the recommendation. (e.g., "Consult Alice; she resolved the last 3 occurrences of this seal leak.")
