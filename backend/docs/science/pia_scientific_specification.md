# PIA Scientific Specification

Welcome to the Scientific Specification for the Predictive Intelligence Architecture (PIA). 
This document serves as the canonical scientific blueprint, detailing the mathematical, algorithmic, and theoretical foundations of the platform.

## Table of Contents
1. [Part 1: System Philosophy](#part-1--system-philosophy)
2. [Part 2: Complete Data Flow](#part-2--complete-data-flow)
3. [Part 3: Mathematical Foundations](03_mathematical_foundations.md)
4. [Part 4: Algorithms](04_algorithms.md)
5. [Parts 5-7: Formulas, Metrics, and Calibration](05_formulas_and_metrics.md)
6. [Parts 8-12: Analysis, Validation, and Future Extensons](08_analysis_and_validation.md)

---

## Part 1 — System Philosophy

### Goals of PIA
PIA aims to transition software engineering from heuristic guesswork into a deterministic, scientifically grounded, and explainable intelligence platform. By measuring structural Git artifacts and mapping them to latent knowledge representations, PIA exposes the hidden physical properties of a software engineering organization.

### Scientific Principles
1. **Deterministic Intelligence**: All measurements must be entirely reproducible, mathematically sound, and free from non-deterministic variance.
2. **Explainability**: Every conclusion, forecast, or health score must be traceable backward via a causal Directed Acyclic Graph (DAG) to immutable physical evidence (a Git commit).
3. **Immutable Truth**: The deterministic pipeline acts as the ground truth. Generative AI layers (Cognitive Runtime) never *compute* truth; they only *synthesize* and *reason* over established deterministic truth.

### Why Deterministic Reasoning Precedes AI Reasoning
LLMs are highly non-deterministic, prone to hallucination, and struggle with strict structural mathematics (e.g., maintaining temporal event graphs). By forcing the platform to compute all physical realities (Observation $\rightarrow$ Measurement $\rightarrow$ Expertise $\rightarrow$ Knowledge $\rightarrow$ Causality $\rightarrow$ Forecast) deterministically, we provide the LLM with a highly constrained, causal context window. The AI acts as an executive advisor operating strictly within the guardrails of mathematical reality.

---

## Part 2 — Complete Data Flow

The canonical pipeline consists of 17 sequential stages, transforming raw repository bits into natural language cognitive insights.

```mermaid
flowchart TD
    Git[Git Repository] --> Obs[Observation]
    Obs --> Meas[Measurement]
    Meas --> Evid[Evidence]
    Evid --> Exp[Expertise]
    Exp --> Know[Knowledge]
    Know --> KG[Knowledge Graph]
    KG --> Temp[Temporal Intelligence]
    Temp --> Forc[Forecasting]
    Forc --> Sim[Counterfactual Simulation]
    Sim --> Opt[Portfolio Optimization]
    Opt --> Org[Organization Intelligence]
    Org --> Caus[Causal Intelligence]
    Caus --> Reas[Reasoning]
    Reas --> Dec[Decision]
    Dec --> Exec[Executive Intelligence]
    Exec --> Cog[Cognitive Runtime]
    
    subgraph Cognitive Runtime
        Cog --> Parse[Semantic Parser]
        Parse --> Ret[Capability Retriever]
        Ret --> Plan[DAG Planner]
        Plan --> ExecDAG[Capability Executor]
        ExecDAG --> Synth[Synthesizer]
        Synth --> Ver[Verification Engine]
    end

### Stage Transitions
1. **Observation**: 
   - *Inputs*: Git commits, files. 
   - *Outputs*: Immutable structured observations. 
   - *Transformations*: AST parsing, physical commit mapping.
2. **Measurement**: 
   - *Inputs*: Observations. 
   - *Outputs*: Bounded physical metrics (velocity, complexity).
3. **Evidence**: 
   - *Inputs*: Measurements. 
   - *Outputs*: Causal evidence with mathematically bounded confidence scores.
4. **Expertise**: 
   - *Inputs*: Evidence. 
   - *Outputs*: Weighted mapping of actors to files.
5. **Knowledge**: 
   - *Inputs*: Expertise models. 
   - *Outputs*: Latent mapping of files to domain concepts.
6. **Knowledge Graph**: 
   - *Outputs*: A localized graph linking actors, files, and concepts.
7. **Temporal Intelligence**: 
   - *Outputs*: Velocity, acceleration, and momentum derived from historical snapshots.
8. **Forecasting**: 
   - *Outputs*: Projected time-series values with computed confidence intervals.
9. **Simulation**: 
   - *Outputs*: Counterfactual branched execution (What-if scenarios).
10. **Optimization**: 
    - *Outputs*: Greedy/Knapsack optimized action portfolios based on resource constraints.
11. **Organization Intelligence**: 
    - *Outputs*: Aggregated systemic risk (Health, Bus Factor, Gini).
12. **Causal Intelligence**: 
    - *Outputs*: DAGs mapping organizational risks to their root physical causes.
13. **Reasoning & Decision**: 
    - *Outputs*: Deterministic heuristics producing recommended action pathways.
14. **Executive & Cognitive Runtime**: 
    - *Outputs*: Semantic summaries and LLM-driven retrieval-augmented chat sessions.
    - *Sub-stages*:
      - **Semantic Parser**: Extracts NLP topics and keywords.
      - **Capability Retriever**: Jaccard matching of topics against tool metadata.
      - **DAG Planner**: Resolves structural prerequisites (requires/produces).
      - **Verification Engine**: Maps LLM claims strictly back to canonical evidence.
