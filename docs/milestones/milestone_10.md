# Milestone 10 - Knowledge Risk Detection

Status: Completed

## Objective

Transform organizational risk metrics into actionable insights.

The system should answer:

* Which modules are risky?
* Why are they risky?
* Which risks should be addressed first?

---

## Architecture

GitHub

↓

Event

↓

Evidence

↓

Time-Aware Expertise

↓

Ownership

↓

Risk

↓

Knowledge Risk

↓

Risk Ranking

---

## Implemented Components

### KnowledgeRisk

Represents an actionable risk assessment for a module.

Fields:

* module_ref
* risk_level
* bus_factor
* ownership_count
* summary

---

### KnowledgeRiskPolicy

Strategy abstraction for transforming risk metrics into actionable assessments.

Responsibilities:

* Interpret organizational risk
* Generate human-readable explanations
* Remain independent from orchestration

---

### BusFactorRiskPolicy

First knowledge-risk implementation.

Inputs:

* BusFactor
* Ownership Count

Outputs:

* KnowledgeRisk

Behavior:

* HIGH risk → knowledge concentration warning
* MEDIUM risk → ownership diversification recommendation
* LOW risk → resilience confirmation

---

### KnowledgeRiskService

Coordinates knowledge risk analysis.

Responsibilities:

* Retrieve ownership information
* Retrieve bus factor information
* Delegate evaluation to a policy
* Return KnowledgeRisk

---

### RiskRankingPolicy

Strategy abstraction for repository-level prioritization.

Responsibilities:

* Rank risk assessments
* Allow future ranking algorithms

---

### DefaultRiskRankingPolicy

Current ranking strategy.

Priority:

HIGH > MEDIUM > LOW

Secondary Sort:

Lower bus factor receives higher priority.

---

### KnowledgeRiskQueryService

Repository-level risk query service.

Responsibilities:

* Rank risk assessments
* Return top risks
* Produce prioritization results

---

## Validation

### Single Module Analysis

Module:

packages/react-devtools-facade/src/DevToolsFacade.js

Result:

Risk Level:

HIGH

Bus Factor:

1

Ownership Count:

1

Summary:

This module depends heavily on a small number of owners. Loss of key contributors may create significant knowledge concentration risk.

---

### Repository Risk Ranking

Validation Dataset:

auth.py

payment.py

analytics.py

Result:

Rank #1

auth.py

HIGH

---

Rank #2

payment.py

MEDIUM

---

Rank #3

analytics.py

LOW

---

## Outcome

PIA can now:

* Detect organizational knowledge risks
* Explain risk causes
* Prioritize risks
* Surface the most dangerous modules

The system has moved from risk measurement to risk intelligence.

---

## Architectural Outcome

Activity

↓

Knowledge

↓

Ownership

↓

Risk

↓

Actionable Insights

↓

Prioritized Risks

---

## Next Milestone

Milestone 11 - Successor Recommendation

Determine who should take over ownership when a primary owner becomes unavailable.
