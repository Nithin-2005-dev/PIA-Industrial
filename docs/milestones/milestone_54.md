# Milestone M54 — Counterfactual Simulation Engine

## Objective

Milestone M54 introduces the **Counterfactual Simulation Engine** as a first-class citizen of the PIA canonical runtime. While M52 and M53 brought temporal awareness and deterministic forecasting based on historical trajectories, M54 extends PIA's capability by allowing it to answer "What if?" questions.

The Simulation Engine provides a framework for generating and evaluating hypothetical futures—such as team member departures, redistributions of ownership, or shifts in engineering practices—without polluting the canonical baseline state. It empowers the downstream Decision layer to proactively prioritize interventions based on simulated impact.

---

# Architectural Principles

The cornerstone of M54 is the strict separation between **scenario generation** and **scenario execution**:
1. **Simulation Engine generates, Platform Runtime executes.** The Simulation Engine itself does not contain business logic for evaluating organizational intelligence or rendering decisions. Instead, it prepares hypothetical scenarios (data), and relies on the canonical pipeline (`PlatformRuntime`) to execute them.
2. **Immutability of the Baseline.** Counterfactual evaluations operate strictly against deep clones of the `PlatformContext`. The canonical state remains pristine.
3. **Deterministic Application.** Interventions are applied as deterministic mutations to the cloned state (e.g., modifying the Knowledge Graph, pruning Expertise Models) before being fed into downstream stages.

---

# Abstractions & Data Structures

M54 introduces several key abstractions in the `app/simulation` package:

### 1. `SimulationScenario` and `SimulationIntervention`
A `SimulationScenario` represents a specific hypothetical future. It consists of human-readable `SimulationAssumption`s and one or more `SimulationIntervention`s. An intervention represents a discrete transformation of the context—for instance, `ContributorDepartureIntervention` removes a specific contributor from the knowledge graph and expertise models.

### 2. `ScenarioContext`
Wraps the full lifecycle of a simulation branch. It holds:
- The `SimulationScenario`.
- The `baseline_context` (for reference).
- The `cloned_context` (mutated by interventions and subsequently processed).
- The `execution_result` (`ScenarioExecutionResult`), which snapshots the state of downstream intelligence metrics once the pipeline branch completes.
- The `comparison` (`ScenarioComparison`), which calculates the delta between the baseline outcome and the simulated outcome.

### 3. `PlatformRuntime.branch()`
The central execution mechanism for simulations. The runtime exposes `branch(baseline_context, scenario)`, which:
1. Performs a safe deep clone of the baseline context (duplicating mutable graphs and lists while keeping singletons shared).
2. Applies the scenario's interventions to the cloned state in-place.
3. Resumes the canonical pipeline execution starting from the `intelligence` stage downward (Intelligence → Reasoning → Decision).
4. Packages the results into the `ScenarioContext`.

---

# Pipeline Integration

The simulation phase sits natively in the pipeline as `SimulationStage` (Stage 07e), immediately after `ForecastingStage` and just before `OrganizationIntelligenceStage`. 

1. **Scenario Generation:** `SimulationStage` identifies relevant counterfactual scenarios to explore (e.g., what if the highest-risk single-point-of-failure leaves?).
2. **Branch Execution:** It invokes `PlatformRuntime.branch()` to compute the future state under these assumptions.
3. **Decision Ranking (Stage 10):** The `DecisionStage` uses the `ScenarioComparisonEngine` to compare the baseline `OrgIntelligenceResult` with the simulation branches. Interventions that project a meaningful improvement (e.g., reducing bus-factor risks, improving health) are surfaced as executable Decisions, ranked by their computed `impact_score`.
4. **Executive Dashboard (Stage 11):** Simulation deltas are reported transparently to executives, providing quantitative backing for organizational recommendations.

---

# Findings & Research Horizons

### Simulation Efficacy
By moving evaluation logic back into the core runtime via branching, PIA guarantees that simulations are evaluated using the *exact same rules* as the real world. A simulation doesn't "guess" the impact of a departure; it mathematically removes the developer and allows the standard `OwnershipService` and `BusFactorService` to realize the void organically.

### Future Work (M55 and Beyond)
- **Generative Scenarios:** Currently, scenarios are pre-defined deterministically. Future milestones could use LLMs to generate bespoke scenarios dynamically based on current repository anomalies.
- **Monte Carlo Simulations:** Expanding the engine to run multi-variant probabilistic simulations to establish confidence intervals over complex interactions.
- **Cost-Benefit Interventions:** Assigning "costs" to interventions (e.g., "Training Developer B takes 3 weeks") to optimize decision pathways for the highest ROI.
