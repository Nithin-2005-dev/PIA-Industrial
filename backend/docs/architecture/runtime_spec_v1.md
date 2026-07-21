# M57/M58 Cognitive Runtime: V1 Specification

## Overview
The Cognitive Runtime acts as the primary orchestrator mapping natural language objectives into strict, deterministic repository analytics via the `PlatformRuntime`. It acts as a safety-first agent loop that explicitly separates data acquisition from reasoning to ensure 100% verifiability. With the M58 Refactor, the runtime shifted from rigid intent-routing to a dynamic, capability-based DAG planning architecture.

## 1. Semantic Query Normalization
All queries pass through the `SemanticQueryParser`. Instead of matching rigid English sentences to heuristic `Goal` enums (e.g. `FIND_PERSON`), the parser extracts high-level semantic meaning using NLP:
- **Topics**: Core themes (e.g. `health`, `ownership`, `risk`, `forecast`)
- **Keywords**: Verbatim terms from the query.
- **Entities**: Discovered components, files, or developers.
- **Intent**: Operational categorization (e.g. `REPOSITORY_QUERY`, `GENERAL_CHAT`).

## 2. Semantic Capability Retrieval
The `CapabilityRetriever` scores the capabilities dynamically via Jaccard-like token matching against each Capability's metadata document (which includes `tags`, `descriptions`, `aliases`, and `names`). It returns the top K `CapabilityCandidate`s to the planner.

## 3. DAG-Based Planning Engine
The `PlanningEngine` maps `CapabilityCandidate` objectives into an `ExecutionGraph`. 
Capabilities are defined by strict `CapabilityContract` objects containing dependencies:
- **`requires`**: Required metrics to run (e.g., `["health_metrics"]`)
- **`produces`**: Output metrics provided (e.g., `["forecast_metrics"]`)

The planner performs a topological depth-first search to resolve dependencies. For example, if a `RiskSimulation` requires `health_metrics`, the planner will automatically queue the `Health` capability to run first.

## 4. Execution & Invariants
The `Executor` consumes the DAG of `ExecutionRequest`s and executes them deterministically.
If successful, it returns a normalized `CapabilityResult` wrapping deterministic execution.
All execution passes through the `InvariantChecker` ensuring hard structural invariants (see `runtime_math.md`).

## 5. Synthesis & Verification
1. **Deterministic Report**: `AnswerBuilder` strictly constructs a textual representation of all successful `CapabilityResult` structures.
2. **LLM Synthesis**: `AdaptiveSynthesizer` optionally rewrites this text for user friendliness.
3. **Verification**: `EvidenceVerificationEngine` extracts claims and structurally ties them to `CapabilityResult.evidence_ids`, ensuring no LLM hallucinations are allowed into the final `ExecutiveResponse`.

## 6. M59 Extension Points
- Semantic Memory interfaces are stubbed out for long-term historical context retention in M59.
- The `ProviderManager` handles arbitrary multi-provider load balancing and failovers.
