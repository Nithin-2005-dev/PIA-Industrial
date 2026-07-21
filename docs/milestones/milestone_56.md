# Milestone 56 — Causal Intelligence & Root Cause Analysis

## Overview

Milestone 56 introduces **Causal Intelligence** as a first-class capability within the PIA Latent Engine, completing the platform's transition from descriptive and predictive analytics into explainable engineering intelligence.

Previous milestones enabled the platform to observe software systems, derive measurements, synthesize evidence, estimate expertise, construct knowledge, build knowledge graphs, analyze historical trends, forecast future states, simulate alternative futures, and optimize intervention portfolios.

However, although PIA could accurately recommend *what* actions should be taken, it still could not explain *why* those recommendations existed.

M56 closes this gap by introducing deterministic causal reasoning built upon canonical evidence, organizational intelligence, historical evolution, forecasting, and simulation outputs.

---

# Motivation

Engineering leaders rarely trust recommendations without understanding the underlying causes.

Questions such as:

* Why is repository health decreasing?
* Why is the Bus Factor predicted to collapse?
* Why should ownership be transferred?
* Why is documentation considered the highest priority?

cannot be answered through measurements or optimization alone.

M56 provides scientifically grounded explanations by constructing causal relationships between organizational signals and exposing evidence-backed root causes for every major recommendation.

---

# Objectives

* Introduce Causal Intelligence as a canonical runtime stage.
* Build deterministic root-cause analysis.
* Explain organizational risks through causal mechanisms.
* Provide evidence-backed explanations.
* Preserve complete lineage and traceability.
* Support explainable executive decision making.
* Prepare the platform for future probabilistic causal models.

---

# Runtime Integration

The canonical runtime becomes:

```text
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
Knowledge Graph
    ↓
Temporal Intelligence
    ↓
Forecasting
    ↓
Counterfactual Simulation
    ↓
Portfolio Optimization
    ↓
Organization Intelligence
    ↓
Causal Intelligence
    ↓
Reasoning
    ↓
Decision
    ↓
Executive Intelligence
```

Causal Intelligence executes immediately after Organization Intelligence so that organizational metrics become the primary inputs to causal analysis.

---

# Architecture

M56 introduces a dedicated `app/causal` package containing:

* Causal Engine
* Causal Ontology
* Causal Semantic Model
* Causal Rule Registry
* Rule Providers
* Causal Hypothesis Engine
* Explanation Engine
* Root Cause Models
* Confidence Models
* Causal Context

The architecture follows the same immutable and deterministic design principles as previous milestones.

---

# Major Components

## Causal Engine

Coordinates the complete causal analysis workflow:

* builds semantic relationships
* evaluates causal rules
* discovers hypotheses
* identifies root causes
* computes confidence
* generates explanations

---

## Causal Ontology

Introduces reusable causal concepts including:

* Structural Causes
* Organizational Causes
* Documentation Causes
* Ownership Causes
* Review Causes
* Knowledge Causes

The ontology enables semantic reasoning beyond simple rule evaluation.

---

## Causal Semantic Model

Instead of constructing an independent graph, M56 augments the existing Knowledge Graph with semantic causal annotations.

This prevents duplication while preserving a single canonical representation of engineering knowledge.

---

## Rule Registry

Causal rules are no longer hardcoded.

The engine now supports pluggable rule providers including:

* Documentation Rules
* Ownership Rules
* Review Rules
* Expertise Rules
* Development Velocity Rules

Additional providers can be registered without modifying the engine.

---

## Hypothesis Engine

The hypothesis engine generates possible explanations from activated causal rules and evaluates them against available evidence.

Only hypotheses supported by sufficient evidence become accepted root causes.

Correlation is never presented as causation.

---

## Explanation Engine

The Explanation Engine transforms technical causal analysis into executive-readable narratives.

Each explanation includes:

* primary cause
* supporting causes
* confidence
* uncertainty
* supporting evidence
* rejected hypotheses
* expected intervention effects

---

# Confidence Propagation

Confidence is decomposed into four independent dimensions:

* Evidence Confidence
* Rule Confidence
* Propagation Confidence
* Overall Confidence

This provides significantly better explainability than a single aggregate confidence value.

---

# Downstream Integration

## Organization Intelligence

Organization Intelligence now exposes:

* Primary Root Cause
* Supporting Evidence
* Confidence
* Causal Mechanism

alongside traditional organizational metrics.

---

## Reasoning

Reasoning now consumes Causal Context.

Recommendations explain not only *what* should happen, but *why*.

---

## Decision Intelligence

Decision generation becomes fully explainable.

Each decision now includes:

* causal rationale
* supporting measurements
* evidence identifiers
* expected organizational improvement
* forecast impact
* confidence breakdown

---

## Executive Intelligence

Executive reports now include a dedicated **Causal Analysis** section.

This presents:

* Root Cause Rankings
* Cause Hierarchy
* Supporting Evidence
* Recommended Intervention
* Why the intervention works
* Expected organizational impact
* Confidence
* Alternative hypotheses

---

# Scientific Contributions

M56 introduces deterministic causal reasoning into Engineering Intelligence.

The platform now answers:

* What happened?
* What is happening?
* What will happen?
* What should we do?
* **Why should we do it?**

Every recommendation is now supported by causal evidence instead of statistical observations alone.

---

# Verification

The milestone introduces dedicated regression tests verifying:

* Runtime registration
* Dependency ordering
* Ontology loading
* Rule registry loading
* Semantic model construction
* Root cause discovery
* Explanation generation
* Confidence propagation
* End-to-end lineage
* Deterministic replay

Regression compatibility with previous milestones (M51–M55) is preserved.

---

# Results

M56 significantly improves the interpretability of the platform.

Major improvements include:

* Explainable engineering recommendations
* Deterministic root-cause analysis
* Semantic causal reasoning
* Evidence-backed executive reports
* Complete causal lineage
* Improved organizational transparency

The platform evolves from **prescriptive engineering intelligence** into an **explainable causal engineering intelligence platform**.

---

# Limitations

Current implementation intentionally remains deterministic.

The following capabilities are deferred to future milestones:

* Bayesian causal inference
* Structural Causal Models (SCM)
* Probabilistic causal graphs
* Online causal learning
* Adaptive intervention learning
* Reinforcement-based policy optimization

---

# Conclusion

Milestone 56 represents one of the most significant architectural advances within the PIA Latent Engine.

By integrating deterministic causal reasoning directly into the canonical runtime, the platform moves beyond prediction and optimization to provide transparent, evidence-backed explanations for every major organizational recommendation.

This milestone establishes the scientific foundation required for future enterprise-scale reasoning, adaptive learning, and autonomous engineering intelligence while maintaining complete determinism, immutability, traceability, and reproducibility throughout the platform.
