# PIA Research Notebook

# Volume I — Foundations

## Chapter 2 — RAM-1.2: Information Space Theory

**Version:** 1.0 (Research Draft)

**Status:** Frozen after Review

---

# 1. Introduction

RAM-1 established that the current Event representation is a lossy abstraction of engineering activity.

However, that conclusion immediately raises a deeper question.

> **What information actually exists inside software engineering?**

This chapter attempts to answer that question from first principles.

Rather than beginning with GitHub, GitLab, Jira, or any existing platform, this chapter studies software engineering itself as an information-generating process.

The objective is to construct a platform-independent information space that completely describes observable engineering activity.

---

# 2. Motivation

Every software engineering platform exposes only part of organizational reality.

GitHub exposes commits.

Slack exposes communication.

Jira exposes planning.

CI/CD exposes deployment.

Documentation systems expose knowledge.

No individual platform contains the complete organizational picture.

Therefore, building PIA around GitHub events alone fundamentally limits inference accuracy.

Instead, PIA requires a generalized observation model capable of incorporating heterogeneous engineering observations.

---

# 3. Research Objective

The central research question is:

> **What observable variables exist in software engineering regardless of the platform used to record them?**

The answer forms the theoretical observation space for future versions of PIA.

---

# 4. Information-Theoretic View

Consider an engineering organization.

Reality continuously generates observable signals.

Examples include:

* writing code
* reviewing code
* discussing architecture
* fixing bugs
* deploying services
* mentoring developers
* writing documentation
* responding to incidents

Each activity generates information.

PIA treats these activities as observations emitted by the underlying organizational state.

Thus, software engineering can be viewed as a continuous information source.

---

# 5. Information Categories

The observable information space can be decomposed into multiple independent categories.

## Identity Information

Describes entities participating in observations.

Examples:

* developer
* reviewer
* maintainer
* team
* repository
* module
* service

Contribution:

Provides entity identification.

Information Richness:

High

Noise:

Low

Stability:

Very High

---

## Temporal Information

Describes when observations occur.

Examples:

* timestamps
* event ordering
* duration
* inactivity periods
* response latency

Contribution:

Captures evolution and temporal dynamics.

Information Richness:

High

Noise:

Low

Stability:

High

---

## Behavioral Information

Describes observable actions.

Examples:

* commit
* review
* merge
* deployment
* rollback
* issue creation
* incident response

Contribution:

Represents observable engineering behavior.

Information Richness:

Very High

Noise:

Medium

---

## Structural Information

Describes software topology.

Examples:

* files
* modules
* packages
* repositories
* services
* dependency graphs

Contribution:

Defines organizational interaction space.

Information Richness:

Very High

Noise:

Low

---

## Semantic Information

Captures meaning rather than activity.

Examples:

* commit messages
* design discussions
* architecture decisions
* issue descriptions
* documentation

Contribution:

Provides contextual understanding.

Information Richness:

Extremely High

Noise:

High

---

## Architectural Information

Describes system organization.

Examples:

* component hierarchy
* design patterns
* service boundaries
* API contracts

Contribution:

Essential for architectural knowledge estimation.

---

## Dependency Information

Examples:

* module dependencies
* package dependencies
* service dependencies
* build dependencies

Contribution:

Determines propagation of knowledge and risk.

---

## Communication Information

Examples:

* Slack discussions
* code review comments
* design meetings
* RFC discussions

Contribution:

Captures implicit organizational knowledge.

---

## Review Information

Examples:

* approvals
* requested changes
* review quality
* review latency

Contribution:

Provides evidence of evaluation capability.

---

## Testing Information

Examples:

* unit tests
* integration tests
* failures
* regressions
* coverage

Contribution:

Provides quality-related observations.

---

## Quality Information

Examples:

* complexity
* maintainability
* reliability
* code smells
* technical debt

Contribution:

Represents software state rather than developer behavior.

---

## Organizational Information

Examples:

* teams
* reporting structure
* ownership assignments
* availability
* responsibilities

Contribution:

Defines organizational context.

---

## Knowledge Transfer Information

Examples:

* mentoring
* onboarding
* documentation
* pair programming
* technical presentations

Contribution:

Direct evidence of organizational learning.

---

## Learning Information

Examples:

* repeated interactions
* skill progression
* technology adoption
* certification
* training

Contribution:

Captures evolution of capability.

---

# 6. Information Richness

Different categories contain different amounts of useful information.

Not every observation contributes equally.

For example:

Changing one documentation page may provide more information about architectural knowledge than modifying one hundred generated files.

Therefore, observation quality should eventually be measured using information theory rather than simple activity counts.

---

# 7. Platform Independence

An important design principle emerges.

The information space must remain independent of any software platform.

GitHub, GitLab, Jira, Azure DevOps, Slack, Confluence, Linear, and internal tooling merely expose different subsets of the same underlying information space.

Thus, PIA should operate on abstract observations rather than platform-specific events.

---

# 8. Information Completeness

Let

Ω

represent the complete observable information space.

Every engineering platform contributes a subset.

Examples:

GitHub ⊂ Ω

Jira ⊂ Ω

Slack ⊂ Ω

Documentation Systems ⊂ Ω

CI/CD Systems ⊂ Ω

Future PIA aims to approximate Ω rather than relying on any single subset.

---

# 9. Research Observations

The investigation produced several important observations.

Observation 1

Software engineering activity extends far beyond source code.

Observation 2

Communication is often more informative than modification.

Observation 3

Knowledge transfer produces observable evidence.

Observation 4

Different observation categories possess different information densities.

Observation 5

Repository mining represents only one projection of organizational activity.

---

# 10. Research Outcome

RAM-1.2 establishes the concept of the **Software Engineering Information Space**.

This space defines the universe of observable variables available for organizational inference.

Future milestones will determine which subsets provide the highest information gain for estimating latent organizational state.

---

# 11. Transition to RAM-2

Having identified the complete observable information space, the next question becomes:

> **What hidden organizational variables are these observations attempting to reveal?**

RAM-2 therefore begins the study of latent organizational knowledge.
