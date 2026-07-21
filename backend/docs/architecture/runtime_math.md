# M57 Cognitive Runtime: Mathematical Specification

## 1. Answer Confidence Computation
The final confidence score of any answer is a normalized `[0, 1]` value, computed as the product of 5 independent probability estimates:

```
Overall Confidence = C_evi * C_ver * C_plan * C_ref * C_reason
```
Where:
- **C_evi (Evidence Coverage)**: Percentage of required topics backed by returned `CapabilityResult`s.
- **C_ver (Verification Score)**: `verified_claims / total_llm_claims`. If purely deterministic, `C_ver = 1.0`.
- **C_plan (Planner Completion)**: Ratio of successfully executed requested capabilities to total requested capabilities.
- **C_ref (Reflection Score)**: `1.0 - (missing_evidence_penalty + contradiction_penalty)`.
- **C_reason (Reasoning Consistency)**: Measured by LLM probability log-likelihoods (stubbed to 1.0 in M57).

## 2. Planner Scoring, Ranking, and DAG Resolution
When retrieving capabilities, the `CapabilityRetriever` evaluates a scoring function for each available `CapabilityCard`:

```
S(c) = w1 * SemanticMatch(c, query) + w2 * PreconditionSatisfaction(c, state) - w3 * Cost(c)
```
- `SemanticMatch`: The Jaccard-like intersection of the NLP-extracted `Query(topics ∪ keywords)` against the Capability's `(tags ∪ aliases ∪ name ∪ description)`.
- `PreconditionSatisfaction`: 1.0 if all `required_measurements` exist, else 0.0.
- `Cost(c)`: Normalized token cost + expected latency.

Capabilities are ranked by `S(c)`. The top candidates (`S(c) > Threshold`) become the `primary_candidates`.

### 2.1 Capability DAG Resolution
The `PlanningEngine` performs a topological Depth-First Search to construct the Execution DAG:
```
DAG_Node(c) = c.contract.requires ∪ { p ∈ CapabilityRegistry | p.contract.produces ∩ c.contract.requires ≠ ∅ }
```
This ensures all prerequisite metrics (e.g. `health_metrics`) are computed prior to dependent operations (e.g. `Forecast`).

## 3. Verification Scoring
For a set of generated claims `[c1, c2, ..., cN]` and deterministic observations `[o1, o2, ..., oM]`:

```
VerificationStatus(c_i) = 
  VERIFIED if ∃ o_j | entails(o_j.summary, c_i)
  PARTIALLY_VERIFIED if ∃ o_j | overlaps(o_j.summary, c_i)
  UNVERIFIED otherwise
```

## 4. Cache Policy
Execution Cache hit occurs iff:
```
hash(Capability.id + arguments_json) == cached_hash
AND Capability.contract.cacheable == True
```

## 5. Formal Runtime Invariants
1. `∀c ∈ Planner.outputs, c.repeatable == False ⇒ c ∉ WorkingMemory.completed_actions`
2. `∀c ∈ Executor.inputs, c.preconditions ⊆ WorkingMemory.facts`
3. `∀c ∈ Verifier.verified_claims, c.evidence_ids ∩ RepositoryMemory.evidence_ids ≠ ∅`
4. `AnswerBuilder.input ⊆ CapabilityResult`
5. `Synthesizer.output_facts ⊆ AnswerBuilder.output_facts`
6. `ExecutionState.confidence ≠ NULL`
7. `Intent.requires_repository == True ⇒ PlatformRuntime.loaded == True`
8. `Intent == GENERAL_CHAT ⇒ PlatformRuntime.loaded == False`
9. `∀c ∈ Executor.executed, c.status != PLANNED`
10. `|Executor.executions| == |AgentObservations|`
