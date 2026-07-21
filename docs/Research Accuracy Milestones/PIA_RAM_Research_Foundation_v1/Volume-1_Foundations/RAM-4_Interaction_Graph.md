# PIA Research Notebook

# Volume I — Foundations

## Chapter 10 — RAM-4: Interaction Theory and the Dynamic Organizational Graph

**Version:** 1.0 (Research Draft)

**Status:** Frozen after Review

---

# 1. Introduction

The previous chapters established that organizational intelligence is latent, dynamic, and distributed across humans, software artifacts, relationships, and organizational context.

However, one fundamental question remained unanswered.

> **What is the fundamental primitive of organizational intelligence?**

Traditional software engineering analytics begins with objects such as

* developers,
* commits,
* files,
* pull requests.

PIA argues that none of these are sufficiently fundamental.

Instead,

the most fundamental observable phenomenon inside an engineering organization is the **interaction**.

This chapter introduces the Interaction Theory of Organizational Intelligence.

---

# 2. Motivation

Consider the following engineering activities.

A developer modifies a module.

A reviewer approves a pull request.

A senior engineer mentors a junior engineer.

A deployment updates a production service.

A test validates a build.

Although these activities appear different,

they share one common property.

Each represents an interaction between entities.

Therefore,

interactions—not commits—form the fundamental observations from which organizational intelligence emerges.

---

# 3. Research Question

The central question of RAM-4 is

> **What is the smallest observable unit capable of explaining organizational intelligence?**

Answering this question determines the mathematical foundation upon which the remainder of PIA is constructed.

---

# 4. Existing Perspective

Most repository mining systems implicitly adopt one of the following primitives.

Developer

↓

Commit

↓

Metric

or

Repository

↓

History

↓

Analytics

These representations are platform-dependent and commit-centric.

They fail to generalize to many engineering activities that occur outside version control systems.

---

# 5. Interaction as the Fundamental Primitive

PIA proposes that the primitive object is

Interaction.

An interaction is defined as

> **A temporally bounded observable relationship occurring between one or more entities that provides evidence regarding the hidden organizational state.**

This definition intentionally avoids any dependence upon specific engineering platforms.

---

# 6. Formal Definition

Every interaction consists of five conceptual components.

Subject

The entity initiating the interaction.

Examples

Developer

Service

Pipeline

AI Agent

---

Predicate

The observable action.

Examples

Modified

Reviewed

Approved

Mentored

Discussed

Merged

Deployed

Documented

---

Object

The entity receiving the interaction.

Examples

Module

Issue

Developer

Service

Document

Test

---

Time

The temporal interval during which the interaction occurred.

---

Context

Additional observable information associated with the interaction.

Examples

Metadata

Complexity

Quality indicators

Semantic attributes

Confidence sources

---

These five components together describe every observable engineering activity.

---

# 7. Examples

Example 1

Developer

MODIFIED

Payments Module

---

Example 2

Reviewer

APPROVED

Pull Request

---

Example 3

Senior Engineer

MENTORED

Junior Engineer

---

Example 4

Pipeline

DEPLOYED

Production Service

---

Example 5

Developer

DOCUMENTED

Architecture Specification

---

All engineering observations reduce naturally to interactions.

---

# 8. Why Commits Are Not Fundamental

Commits represent only one specialized interaction.

Developer

↓

Modified

↓

Repository

Many equally important interactions never produce commits.

Examples

Architecture discussions

Design reviews

Mentoring

Incident response

Knowledge sharing

Operational support

Therefore,

commits cannot serve as the universal observation primitive.

---

# 9. Dynamic Interaction Graph

Once interactions become the primitive,

the organization naturally becomes a graph.

Vertices

represent entities.

Edges

represent interactions.

Unlike conventional graphs,

both vertices and edges evolve continuously through time.

Therefore,

PIA introduces the concept of a

Dynamic Interaction Graph.

---

# 10. Components of the Graph

The graph contains heterogeneous entities.

Examples

Developers

Modules

Repositories

Services

Issues

Reviews

Documents

Teams

Pipelines

Tests

Future systems may introduce additional entity types without modifying the mathematical framework.

---

# 11. Interaction Types

Different interaction types contribute different organizational information.

Examples

Development

Review

Communication

Deployment

Testing

Learning

Documentation

Planning

Operations

Therefore,

interaction type becomes a first-class component of organizational inference.

---

# 12. Relationship State

Every edge within the interaction graph possesses latent properties.

Examples

Familiarity

Knowledge transfer

Ownership tendency

Interaction strength

Trust

Collaboration quality

Unlike traditional graphs,

edges contain hidden organizational state rather than merely indicating connectivity.

---

# 13. Temporal Evolution

The interaction graph changes continuously.

New interactions

create edges.

Repeated interactions

strengthen edges.

Long inactivity

weakens certain relationships.

Organizational restructuring

modifies graph topology.

Therefore,

the interaction graph represents a dynamic organizational process rather than a static network.

---

# 14. Advantages

Modeling organizations through interactions provides several important advantages.

Platform Independence

The model applies equally to GitHub,

GitLab,

Jira,

Slack,

Azure DevOps,

or future engineering platforms.

---

Unified Representation

Every engineering activity shares one mathematical representation.

---

Extensibility

New observation types become additional interaction predicates rather than architectural changes.

---

Future Compatibility

The graph naturally supports graph algorithms,

probabilistic inference,

and machine learning.

---

# 15. Comparison with Existing Repository Mining

Traditional Repository Mining

Primitive

Commit

Representation

Repository History

Primary Focus

Code Activity

---

PIA

Primitive

Interaction

Representation

Dynamic Organizational Graph

Primary Focus

Latent Organizational Intelligence

This distinction fundamentally changes the scope of organizational analysis.

---

# 16. Research Contributions

RAM-4 establishes the following principles.

### Principle 1

The interaction is the fundamental observable unit of organizational intelligence.

---

### Principle 2

Commits represent only one specialized interaction type.

---

### Principle 3

Organizations can be represented as dynamic interaction graphs.

---

### Principle 4

Interactions provide evidence rather than organizational truth.

---

### Principle 5

Every future observation source can be integrated by introducing new interaction predicates.

---

# 17. Remaining Challenge

Although the interaction graph provides an elegant structural representation,

it does not explain

how hidden organizational state evolves.

The graph represents

structure.

It does not represent

state estimation.

A mathematical framework is therefore required to describe how interactions modify latent organizational state over time.

---

# 18. Transition to RAM-5

The next chapter introduces the complete Organizational State Theory.

Rather than viewing the organization simply as a graph,

RAM-5 integrates

* Human State,
* Artifact State,
* Relationship State,
* Organizational Context,

into a unified dynamic latent state evolving over the interaction graph.

This chapter marks the transition from structural representation toward formal state-space modeling.

---

# Chapter Summary

RAM-4 establishes the Interaction Theory of Organizational Intelligence.

By identifying interactions as the fundamental observable primitive,

PIA becomes independent of commits,

repositories,

and engineering platforms.

The resulting Dynamic Interaction Graph provides a unified mathematical representation capable of modeling heterogeneous engineering observations while supporting future probabilistic inference.

This chapter completes the structural foundation of PIA and prepares the transition toward formal latent state modeling.
