# Part 4: Algorithms

## Expertise Estimation

**Intuition**: We must map an actor's raw commit activity into a domain-bounded expertise score that decays over time if they leave the project.

**Pseudocode**:
```text
function EstimateExpertise(commits, target_file):
    score = 0
    for commit in commits touching target_file:
        time_diff = NOW - commit.date
        decay_factor = exp(-LAMBDA * time_diff)
        weight = commit.complexity * decay_factor
        score += weight
    return min(100, log_scale(score))
```

**Complexity**: $O(C \times F)$ where $C$ is commits and $F$ is files modified.
**Correctness**: Correctly weights temporal proximity. Bounded asymptotically.
**Limitations**: Assumes all Lines of Code (complexity) require equal cognitive effort.

---

## Forecast Engine

**Intuition**: Future states are best predicted by analyzing historical structural velocity and applying variance-based confidence decay.

**Pseudocode**:
```text
function Forecast(series, horizons):
    model = SelectBestModel(series)
    for h in horizons:
        prediction = model.project(h)
        variance = model.compute_variance()
        base_confidence = min(1.0, length(series) / 10.0)
        cv = sqrt(variance) / mean(series)
        confidence = base_confidence * exp(-0.5 * cv) * exp(-0.01 * h)
        yield (prediction, confidence)
```

**Complexity**: $O(N)$ where $N$ is the length of the time series for smoothing models. $O(N \log N)$ or $O(N^2)$ for complex OLS constraints.
**Correctness**: Statistically sound bounds on uncertainty utilizing CV.
**Limitations**: Cannot predict step-function changes (e.g., massive refactors).

---

## Causal Rule Engine

**Intuition**: When an organization-level metric fails (e.g., Health = CRITICAL), we must traverse the dependency DAG to find the physical file causing the drop.

**Pseudocode**:
```text
function RootCause(risk_node):
    causes = []
    for edge in DAG.inbound_edges(risk_node):
        if edge.weight > THRESHOLD:
            cause_node = edge.source
            if is_physical(cause_node):
                causes.append(cause_node)
            else:
                causes.extend(RootCause(cause_node))
    return sort(causes, by=edge.weight)
```

**Complexity**: $O(V + E)$ DAG traversal.
**Correctness**: Assumes DAG is strictly acyclic and edge weights denote true causal probability.
**Limitations**: Latent confounding variables (e.g., external team restructuring) are invisible to the physical graph.

---

## Planner

**Intuition**: Instead of executing all tools, the Cognitive Runtime creates a directed retrieval plan.

**Pseudocode**:
```text
function Plan(user_query, capability_registry):
    plan_steps = []
    semantic_intent = LLM.extract_intent(user_query)
    for cap in capability_registry:
        if matches(semantic_intent, cap.domain):
            plan_steps.append(cap.command)
    return topological_sort(plan_steps)
```

**Complexity**: $O(R \log R)$ where $R$ is registry capabilities.
**Correctness**: Decouples intent mapping from execution, ensuring LLM hallucinations cannot trigger unregistered actions.
**Limitations**: LLM intent extraction is non-deterministic.
