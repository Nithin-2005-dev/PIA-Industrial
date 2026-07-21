# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - PIA Industrial Hackathon Prototype

### Added
- **Industrial Ontology**: Introduced core domain objects including Assets, Components, Inspections, Failures, and Maintenance events.
- **Document Intelligence**: Capable of ingesting unstructured technical manuals, shift logs, and maintenance records.
- **Knowledge Graph**: Replaced relational dependencies with an in-memory NetworkX-based Industrial Knowledge Graph to connect asset facts temporally and hierarchically.
- **Hybrid Retrieval**: Combines semantic vector searches with deterministic graph traversal.
- **Asset Intelligence**: 360-degree timeline generation for specific industrial equipment (e.g. Pump P-101).
- **Causal RCA**: New deterministic root cause analysis engine that calculates causal hypotheses based on precursor events (e.g. vibrations preceding bearing failures).
- **Counterfactual Simulation**: Graph-based engine to simulate the consequences of delayed maintenance interventions.
- **Compliance Intelligence**: Evaluates compliance risk deterministically against required inspection frequencies.
- **Expertise Intelligence**: Maps critical operational knowledge to specific engineers based on historical interventions.
- **Decision Intelligence**: Prioritizes asset interventions based on calculated multi-variable risk.
- **Industrial UX**: Re-themed and structured the presentation layer to support industrial asset monitoring and the Copilot interaction.
