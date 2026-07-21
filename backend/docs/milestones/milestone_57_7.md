# Milestone 57.7: Cognitive Observability & Reflection Loop

## Architecture
Introduces `CognitiveTrace` for every stage. `ExecutionState` is now immutable.

## Policy Interactions & Reasoning Flow
Planner -> Executor -> Context -> Orchestrator -> Reflection -> `should_replan`.
If `should_replan`, loop repeats up to 3 times or until confidence stabilizes.

## Limitations
JSON trace files can grow large for long-running hybrid sessions.

## Future Extensions
Time-travel debugging UI, streaming observability graphs.
