# PIA Research Notebook

# Volume I — Foundations

## Chapter 4 — RAM-2.1: Mathematical Structure of Organizational Knowledge

**Version:** 1.0 (Research Draft)

**Status:** Frozen after Review

---

# 1. Introduction

The previous chapter established that organizational knowledge is a latent variable that cannot be directly observed.

However, that conclusion immediately raises a deeper question.

> **What exactly is organizational knowledge?**

Before designing inference algorithms, it is necessary to determine the mathematical object that knowledge represents.

Is knowledge

* a scalar,
* a vector,
* a graph,
* a probability distribution,
* or an entirely different mathematical object?

The purpose of this chapter is to investigate the internal structure of knowledge from first principles.

---

# 2. Motivation

Current expertise estimation systems almost universally represent knowledge using a single numerical score.

Examples include

* expertise score
* ownership score
* contribution score
* familiarity score

Although convenient,

this assumption has never been rigorously justified.

PIA therefore challenges this assumption.

---

# 3. Research Question

The central research question of this chapter is

> **What mathematical object best represents software engineering knowledge?**

---

# 4. Candidate Model I — Scalar Knowledge

The simplest assumption is

Knowledge = One Number

Mathematically

K ∈ ℝ

Example

Developer A

Payments Module

Knowledge = 0.82

Advantages

* simple
* computationally efficient
* easy to rank

Limitations

Cannot distinguish

* architectural understanding
* debugging capability
* implementation experience
* historical understanding

Different knowledge types become compressed into one value.

---

# 5. Thought Experiment

Consider three developers.

Developer A

Designed the architecture.

Developer B

Maintains production daily.

Developer C

Reviews every pull request.

If knowledge is scalar,

one developer must possess

more

knowledge than the others.

However,

human experts generally disagree.

Each developer possesses

different

knowledge.

Therefore

scalar representation loses important information.

---

# 6. Candidate Model II — Vector Knowledge

Instead of

one number,

knowledge becomes

a vector.

K = (k₁, k₂, ..., kₙ)

Each component represents an independent aspect of understanding.

This allows different developers to possess different knowledge profiles.

---

# 7. Candidate Knowledge Dimensions

Several dimensions naturally emerge from software engineering.

## Structural Knowledge

Understanding of

* files
* packages
* services
* dependencies

---

## Functional Knowledge

Understanding of

* business rules
* algorithms
* workflows
* APIs

---

## Architectural Knowledge

Understanding of

* system design
* component interactions
* constraints
* design decisions

---

## Historical Knowledge

Understanding of

* why code exists
* previous bugs
* design evolution
* technical debt

---

These dimensions are conceptually distinct and evolve independently.

---

# 8. Candidate Model III — Knowledge Graph

Knowledge could also be represented as a graph.

Nodes

Concepts

Edges

Relationships

Advantages

Captures rich semantic relationships.

Disadvantages

Difficult to estimate continuously.

High computational complexity.

Not immediately suitable for probabilistic state estimation.

---

# 9. Candidate Model IV — Probability Distribution

Knowledge represented as

P(K)

Advantages

Explicit uncertainty.

Natural Bayesian interpretation.

Disadvantages

Distribution alone does not describe internal structure.

Probability models belief,

not knowledge itself.

---

# 10. Comparative Analysis

| Model                    | Expressiveness | Interpretability | Scalability | Suitability              |
| ------------------------ | -------------- | ---------------- | ----------- | ------------------------ |
| Scalar                   | Low            | High             | Excellent   | Poor                     |
| Vector                   | High           | High             | Good        | Excellent                |
| Graph                    | Very High      | Medium           | Moderate    | Future Research          |
| Probability Distribution | High           | Medium           | Good        | Complements other models |

---

# 11. Research Observation

Knowledge itself possesses internal structure.

Probability represents uncertainty about knowledge,

not knowledge itself.

Therefore,

knowledge and uncertainty should not be merged into a single mathematical object.

---

# 12. Research Hypothesis

PIA proposes the following hypothesis.

> **Software engineering knowledge is a multidimensional latent variable rather than a scalar quantity.**

Each dimension evolves independently,

is observed differently,

and contributes differently to organizational decision making.

---

# 13. Consequences

Replacing scalar knowledge with vector knowledge has profound implications.

Current Systems

Developer

↓

Expertise Score

Future PIA

Developer

↓

Knowledge Vector

↓

Inference

↓

Decision Functions

Ownership,

risk,

forecasting,

and mentoring

can now depend upon different dimensions of knowledge rather than a single score.

---

# 14. Remaining Questions

Although vector representation solves many limitations,

important questions remain.

Should capability be part of knowledge?

Does knowledge imply ability?

Can someone possess architectural knowledge while lacking implementation capability?

These questions motivate the next research milestone.

---

# 15. Transition to RAM-2.2

The next chapter investigates one of the most important distinctions within organizational intelligence.

> **Is knowledge equivalent to capability?**

Answering this question determines whether PIA estimates one latent variable or multiple interacting latent variables.

---

# Chapter Summary

RAM-2.1 rejects the assumption that organizational knowledge can be represented by a single scalar.

Instead,

it proposes that knowledge is inherently multidimensional and that different dimensions contribute differently to engineering decisions.

This chapter lays the mathematical foundation for the separation of knowledge, capability, and uncertainty developed in the following milestones.
