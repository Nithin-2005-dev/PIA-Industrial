# M31 — Observation Layer

# 01_Motivation.md

---

# Motivation

## Background

The original PIA architecture was designed to transform software engineering events into evidence that could later be used to estimate organizational knowledge. During the early stages of development, this objective was achieved by extracting a small number of handcrafted attributes from GitHub commits, such as commit messages, code churn, and total line changes. These extracted attributes were then passed directly into the evidence generation pipeline.

This architecture provided a simple and efficient implementation, but it revealed a fundamental limitation during the mathematical development of the PIA framework.

The system was compressing observations before reasoning about them.

As a consequence, a large portion of the information available from the original software engineering event was permanently discarded before any inference algorithm had an opportunity to evaluate its importance.

---

# Problem Statement

Consider a GitHub commit.

The GitHub REST API returns a rich observation containing information such as:

* commit identity
* commit ancestry
* author and committer identities
* timestamps
* verification status
* modified artifacts
* file-level statistics
* code patches
* repository metadata
* URLs
* provenance information

However, the original Event model retained only a very small subset of these facts:

* SHA
* commit message
* additions
* deletions
* total changes

Everything else was discarded during normalization.

Although this simplification allowed the first version of PIA to function correctly, it introduced an important architectural weakness:

> Future inference algorithms could only reason over compressed observations rather than complete observations.

Once discarded, information cannot be recovered without performing another expensive interaction with the external platform.

---

# Research Question

The research question addressed by M31 is therefore:

> Can an intelligence system preserve complete engineering observations while remaining fully backward compatible with an existing inference pipeline?

This question is significant because modern probabilistic inference systems benefit from richer evidence. If observations are compressed too early, later mathematical models are forced to reason using incomplete information.

---

# Hypothesis

M31 is based on the following hypothesis.

**Hypothesis**

If every observable engineering fact is preserved before inference begins, then future probabilistic and information-theoretic algorithms can construct significantly richer evidence than systems that discard information during normalization.

This hypothesis does not claim that preserving information immediately increases prediction accuracy.

Instead, it claims that information preservation expands the hypothesis space available to future inference algorithms.

---

# Design Philosophy

The design philosophy introduced in M31 is summarized by a single principle:

> Preserve facts first. Interpret them later.

Observation is responsible only for recording facts that were directly observed.

Interpretation belongs to later layers of the architecture.

This separation produces a cleaner mathematical model because it prevents assumptions, heuristics, and probabilistic reasoning from contaminating the original observation.

---

# Previous Architecture

Before M31 the data flow was approximately:

GitHub

↓

Normalization

↓

Evidence

↓

Knowledge Estimation

Although computationally efficient, this architecture permanently removed large amounts of information during normalization.

---

# M31 Architecture

M31 introduces an intermediate observation layer.

GitHub

↓

Observation

↓

Measurement

↓

Evidence

↓

State Estimation

The Observation Layer becomes the permanent repository of immutable engineering facts.

Future inference algorithms never need to consult GitHub again because every observable fact has already been preserved.

---

# Objectives

The primary objectives of M31 are:

1. Preserve observable engineering facts.
2. Introduce a structured Observation Space.
3. Maintain complete backward compatibility.
4. Avoid modifying existing inference logic.
5. Prepare the architecture for probabilistic reasoning.

---

# Scope

M31 intentionally does **not** introduce:

* Bayesian inference
* machine learning
* confidence estimation
* semantic classification
* expertise prediction
* ownership estimation

These remain responsibilities of future milestones.

M31 focuses exclusively on preserving observations.

---

# Expected Benefits

The Observation Layer provides several long-term advantages.

## Information Preservation

Observable information is retained instead of discarded.

## Reproducibility

Every inference can be reproduced from the preserved observations.

## Extensibility

Future algorithms may use information that was unknown or unnecessary during M31.

## Backward Compatibility

Existing evidence extraction remains unchanged.

## Mathematical Separation

Observation, Measurement, Evidence and State Estimation become distinct mathematical spaces rather than being mixed together.

---

# Conclusion

M31 represents a fundamental architectural transition within PIA.

Rather than viewing software engineering events as compressed records, the system now treats them as complete engineering observations.

This change does not immediately increase inference accuracy.

Instead, it establishes the mathematical and architectural foundation required for all future probabilistic reasoning performed by the PIA framework.
