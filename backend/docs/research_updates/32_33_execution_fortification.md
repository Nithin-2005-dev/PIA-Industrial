# Phase 32 & 33: Execution Pipeline Fortification

## Context and Architecture Risk
During our final security sweep of the Evidence Layer, two execution landmines were identified which posed an existential risk to the platform:

1. **The Event Cascade Trap (CPU Meltdown)**
   The `RankingService` uses PageRank which operates at $O(V \times E)$ complexity. If PageRank were executed synchronously on the `EvidenceUpdate` event bus, then during a mass PR merge, `N` independent edges could trigger `N` concurrent PageRank simulations. This would instigate an OOM death spiral and catastrophically crash the computation cluster.
   
2. **The Transitive Liability Trap**
   The original `KnowledgeRiskService` calculated Bus Factor locally on isolated modules. However, in an enterprise graph, a structurally flawless module can inherit systemic vulnerability if it strictly depends on an undocumented, highly fragile upstream component. Failing to account for recursive N-hop dependencies results in false security dashboards that conceal single-points-of-failure.

## Implementation: Phase 32 (Scheduler Batching)

### Architectural Decision
**We decoupled all heavy graph algorithms from the real-time event pipeline.** 

### Execution
1. Created `NightlyAnalysisJob` in `app/platform/jobs/analysis_job.py`.
2. Registered the job inside `IntelligencePlatformModule` via Dependency Injection.
3. Hooked `NightlyAnalysisJob` into the global `Scheduler` inside `BuiltPlatformRuntime.start()`.
4. Hardcoded execution schedule to a nightly Cron (`0 0 * * *`).

### Result
Real-time measurements will simply execute $O(1)$ appends to the Evidence Graph. At midnight, `NightlyAnalysisJob` performs a single, highly efficient traversal across the materialized graph to resolve global Structural Authority and Knowledge Risks.

## Implementation: Phase 33 (Transitive Risk Bubbling)

### Architectural Decision
**A node's true risk is the maximum between its intrinsic risk and the risk of all downstream dependencies it relies on.**

### Execution
1. Upgraded `KnowledgeRiskService.analyze` to invoke a new recursive `analyze_transitive_risk` method.
2. Injected `GraphService` into `KnowledgeRiskService`.
3. Executed N-hop topological recursion utilizing `DEPENDS_ON` relationships via `self._graph_service.outgoing()`.
4. Integrated a `visited` state map to safely short-circuit graph cycles (infinite loop prevention).
5. Built mathematical verification in `tests/test_transitive_risk.py` asserting risk bubbles appropriately from upstream nodes.

### Result
The Dashboard will correctly flag a critical security module as "HIGH RISK" if its upstream database connector possesses a Bus Factor of 1, exposing true fragility vectors to enterprise executives.
