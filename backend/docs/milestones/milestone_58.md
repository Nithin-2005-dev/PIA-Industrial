# Milestone 58: Capability-Based Planning Architecture

## Overview
Milestone 58 refactors the Cognitive Runtime's routing mechanism. It transitions the platform from a rigid, regex-based intent routing system into a dynamic, Capability-Based Planning architecture using Directed Acyclic Graphs (DAGs) and Semantic Retrieval.

## Key Changes

1. **Semantic Query Normalization**
   Instead of forcing user queries into predefined `Goal` enums, the `SemanticQueryParser` extracts pure NLP `topics` and `keywords` from the raw input.
   
2. **Semantic Capability Retrieval**
   The `CapabilityRetriever` scores registered capabilities using Jaccard-like intersection of the query's NLP components against the Capability's `tags`, `aliases`, `name`, and `description`.

3. **DAG-Based Planning Engine**
   The `PlanningEngine` evaluates the top semantic matches and constructs an execution DAG by resolving structural dependencies defined in the capability contracts (`requires` and `produces`).
   
4. **Execution Queue**
   The `Executor` now consumes the topologically sorted DAG of capabilities instead of isolated intent requests.

## Rationale
This ensures that the runtime scales infinitely as more tools are added to the `CapabilityRegistry`. The LLM reasoning layers can now rely on a robust semantic discovery mechanism instead of hardcoded heuristic mappings.
