# Milestone 51 - Platform Runtime Unification

## Previous Architecture

The showcase owned a parallel execution path. It imported each pipeline stage,
constructed services directly in several stages, and built a NetworkX knowledge
graph locally before organization intelligence consumed that shape.

## Unified Architecture

`PlatformRuntime.run(...)` is now the canonical execution entry point. The
runtime registers core modules, builds DI, starts lifecycle management, emits
runtime events, executes the canonical pipeline, and returns stable runtime
contracts.

Canonical stage flow (11 stages):

```
GitHub
  ↓
Observation
  ↓
Measurement
  ↓
Evidence
  ↓
Expertise
  ↓
Knowledge
  ↓
Knowledge Graph          ← first-class runtime stage (graph module)
  ↓
Organization Intelligence
  ↓
Reasoning
  ↓
Decision
  ↓
Executive Intelligence
```

Knowledge Graph is a **first-class runtime stage**, not an internal
implementation detail.  It is registered as the `graph` module, receives a
canonical `CanonicalStageBinding`, emits `runtime.stage.started` /
`runtime.stage.completed` events, appears in `RuntimePipelineResult.completed_stages`,
and is validated by Pipeline Validation (Stage 12) along with every other layer.

## Runtime Flow

1. `PlatformRuntime.register_default_modules()` registers subsystem modules.
2. `ModuleRegistry.startup_order()` determines dependency order.
3. `CanonicalPlatformPipeline` writes the full execution plan to
   `context.metrics["execution_order"]` and
   `context.metrics["execution_stage_names"]` **before** any stage runs.
4. Each binding declares input contract, output contract, module, and version.
5. Runtime events are emitted for pipeline start, stage start, stage completion,
   stage failure, and pipeline completion.
6. `RuntimePipelineResult` preserves completed stages, errors, execution order,
   and the final context.

## Pipeline Validation Contract

`PipelineValidationStage` (Stage 12) reads `context.metrics["execution_stage_names"]`
to render the Actual Execution Path section.  The path is always derived from
the runtime execution plan — never from a hand-maintained list.  This ensures
that every stage that executes also appears in the validation output.

## Migration Strategy

The first consolidation moved orchestration authority from
`scripts.platform_showcase.pipeline` into `app.platform.runtime`. The showcase
now subscribes to runtime events and renders progress/results.

Measurement, evidence, GitHub collection, and knowledge graph construction are
resolved through DI-backed runtime services. The graph stage now calls the
canonical `KnowledgeGraphBuilder` rather than constructing NetworkX directly.

## Removed Duplication

- Showcase-owned stage ordering was removed.
- Direct measurement engine construction was replaced by runtime DI.
- Direct evidence synthesis construction was replaced by runtime DI.
- Direct NetworkX graph construction was replaced by canonical graph building.
- Knowledge and organization intelligence are explicit runtime modules.
- Reasoning now precedes decision in the dependency graph.
- Pipeline Validation now derives its output from the runtime, not a static list.

## Dependency Graph

```
observation → measurement → evidence → estimation → knowledge → graph →
intelligence → agent → decision → executive
```

`intelligence` (Organization Intelligence) depends on `graph` (Knowledge Graph).
`graph` depends on `knowledge`. No hidden dependencies exist.

Forecasting and simulation remain registered platform capabilities and are
available to downstream services, but they no longer control the canonical
showcase execution path.

## Lessons Learned

The platform already had strong subsystem services, but the showcase had become
an accidental second runtime. The important architectural move is to make future
features register modules and services with `PlatformRuntime`, then let runtime
contracts and events expose execution state to CLI, tests, APIs, and UI.

The M51 follow-up (M51b) identified that reporting surfaces (Pipeline
Validation, Executive Lineage, and the Canonical Architecture Banner) had
diverged from the actual runtime because they were maintained as independent
hardcoded lists.  The fix was to make every reporting surface derive its output
from `context.metrics["execution_stage_names"]` — the single source of truth
written by `CanonicalPlatformPipeline` before any stage executes.
