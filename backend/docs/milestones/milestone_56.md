# Milestone 56: Causal Intelligence & Root Cause Analysis Engine

## Overview

M56 transforms the PIA Latent Engine from a prescriptive platform into a causal intelligence platform. Prior to M56, the platform could recommend actions based on observed organizational states (e.g., "high bus factor"), but it could not explain *why* those states existed. M56 adds a fully determinable Causal Intelligence layer that explains the organizational state via root-cause analysis.

## Architecture

The Causal Intelligence layer executes immediately after Organization Intelligence and before Reasoning. This is architecturally critical:
1. `Organization Intelligence` computes empirical signals (bus factor, health, coverage).
2. `Causal Intelligence` explains why those signals are what they are.
3. `Reasoning` consumes both to produce enriched conclusions.
4. `Decision` builds causally-justified recommendations.

## Semantic Model

Instead of building a separate graph, Causal Intelligence introduces the `CausalSemanticModelBuilder`. It builds a semantic overlay on top of the existing Knowledge Graph:
- `CausalNode`: Wraps existing entities with observed states and trends.
- `CausalEdge`: Captures the declared causal relationship between nodes.
- `CausalAnnotation`: Tags existing Knowledge Graph nodes with causal metadata.

## Ontology & Rule Registry

Causal mechanisms are not ad-hoc strings. They are defined in the `CausalOntology` (e.g., `ownership_concentration`, `review_diversity_decline`) which supports ancestor traversal and category-level aggregation.

Rules are managed via a `CausalRuleRegistry` that consumes `RuleProvider` implementations. There are 13 core rules across 5 providers (Documentation, Ownership, Review, Expertise, Velocity).

## Explanation Engine

The `ExplanationEngine` synthesizes the `CausalHypothesisEngine` results into human-readable narratives. Confidence is explicitly decomposed into four vectors:
- **Evidence Confidence**: How strongly do we believe the underlying measurement?
- **Rule Confidence**: How strongly do we believe the declared causal mechanism?
- **Propagation Confidence**: How much confidence is lost traversing the causal chain?
- **Overall Confidence**: The aggregated score.

## Lineage & Traceability

Every generated `RootCause` maintains strict lineage back to canonical `Observation` objects. The `stage12_validation.py` pipeline verifies that no "orphan" explanations exist. If a root cause is claimed, it must be supported by pipeline evidence.

## Limitations & Future Extensions (M57+)

Currently, the Causal Engine uses Level 1 (observational) deterministic rules. In future milestones (M59+), this will be extended to a Bayesian Network (BN) where conditional probability tables (CPTs) are learned from historical data rather than declared via fixed rules.
