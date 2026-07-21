# Milestone 56 Research Findings
## Causal Intelligence & Root Cause Analysis in Engineering Contexts

### 1. Structural Causal Models (SCMs)
Judea Pearl's Structural Causal Models form the theoretical foundation for M56. While SCMs typically involve learning probability distributions over DAGs, M56 implements a deterministic Level-1 observational causal model. This was chosen because engineering signals (like Bus Factor or Coverage) are fully observable deterministic outcomes of source control events, making probabilistic guessing unnecessary for structural causality.

### 2. Engineering Root Cause Analysis
Root Cause Analysis (RCA) in software engineering is traditionally retrospective (e.g., analyzing a production outage). M56 shifts RCA to be proactive and continuous. By applying causality to *organizational health* rather than just system uptime, we can trace knowledge risks back to behavioral anti-patterns (like Review Diversity Decline) before they manifest as critical failures.

### 3. Explainable AI (XAI)
A core tenet of XAI is that explanations must be actionable. M56 achieves this by decomposing confidence into Evidence, Rule, and Propagation segments. When an executive sees a 95% confidence score, they can drill down to see exactly which piece of evidence (e.g., a specific pull request or ownership overlap) drove that score, satisfying DARPA's XAI requirements for transparent systems.

### 4. Causal Graphs and Ontologies
M56 avoids building a separate, disconnected causal graph. Instead, it uses a Semantic Overlay on the existing Knowledge Graph. The `CausalOntology` standardizes mechanisms into 5 categories (Structural, Behavioral, Process, Documentation, Organizational). This ensures that causal reasoning is strictly bounded and category-queryable, preventing "hallucinated" or ad-hoc causal relationships.

### 5. Deterministic Causal Reasoning
We explicitly opted for deterministic rules via a `RuleRegistry` rather than machine learning models. The lack of standardized, cross-company historical training data for "organizational health failures" makes supervised learning unviable. Deterministic rules (e.g., Bus Factor < 2 AND Ownership > 80% => High Knowledge Risk) provide 100% auditability.

### 6. Lessons Learned
- **Causal Chains Branch**: Real causality in engineering is a DAG, not a straight line. Multiple distinct root causes (like poor documentation AND high attrition) converge on a single effect.
- **Traceability is Hard but Essential**: Enforcing that every causal hypothesis must link to a specific `evidence_id` in the pipeline was difficult to wire, but it prevents the AI from generating plausible-sounding but completely ungrounded explanations.

### 7. Remaining Research Gaps
- **Level-2 Interventional Causality**: While M54 does counterfactual simulation, formally integrating it into the causal engine via do-calculus (`P(Y | do(X))`) remains for a future milestone.
- **Bayesian Probabilistic Extension**: When the system accumulates enough historical snapshots across multiple tenants, the deterministic rules can be swapped for a learned Bayesian Network.
