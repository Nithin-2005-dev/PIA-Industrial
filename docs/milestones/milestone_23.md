# M23 - Agent Grounding Phase 1

## Goal

Connect the Organizational Reasoning Agent to the real intelligence engine instead of fixture-backed adapters.

---

## Problem

Previous agent capabilities were demonstration-only.

Although M1-M22 produced expertise, ownership, risk, successor, transfer, health, forecast, and simulation intelligence, the agent answered questions using handcrafted reports and sample data.

Architecture before M23:

Question
→ Intent Classification
→ Adapter
→ Hardcoded Fixtures
→ Response

The intelligence engine existed, but the agent was not connected to it.

---

## Implemented

### M23.1 Context Extraction

Added extraction of module references from user questions.

Examples:

* Who should take over auth.py?
* Why is payments.py risky?
* Which developer should we train for auth.py?

Adapters can now receive module-specific context.

---

### M23.2 Transfer Intent

Added Transfer intent detection and routing.

Examples:

* Which developer should we train next?
* Where should we invest knowledge transfer?
* Who is the best mentor?

---

### M23.3 IntelligenceContext

Introduced a composition root:

IntelligenceContext

Responsibilities:

* ExpertiseQueryService
* OwnershipService
* SuccessorService
* CoverageService
* ConcentrationService
* BusFactorService
* HealthService
* TransferService

This became the central assembly layer for agent-grounded intelligence.

---

### M23.4 Grounded Successor Adapter

Replaced fixture ownership data with:

Projection
→ Query
→ Ownership
→ Successor

Agent answers now originate from real expertise and ownership intelligence.

---

### M23.5 Grounded Transfer Adapter

Replaced fixture mentor/learner recommendations with:

Ownership
→ Successor
→ Concentration
→ Transfer

Agent transfer recommendations now originate from real organizational knowledge distribution.

---

### M23.5.1 Transfer Policy Bug Fix

Grounding exposed a defect in SimpleTransferPolicy.

Issue:

Ownership records were stored in a dictionary keyed by module id, causing later owners to overwrite earlier owners.

Result:

Mentor selection incorrectly returned the last owner instead of the primary owner.

Fix:

Select the owner with the highest ownership percentage per module.

Example:

Before:
Mentor = charlie

After:
Mentor = alice

---

### M23.6 Grounded Risk Adapter

Replaced fixture risk reports with:

Projection
→ Coverage
→ Concentration
→ Bus Factor
→ Health

Agent risk answers now originate from real organizational health calculations.

Example output:

Coverage: 30.00
Concentration: 0.95
Health: 19.00
Level: CRITICAL

---

## Architecture After M23

Question
→ Context Extraction
→ Reasoning Agent
→ Grounded Adapter
→ IntelligenceContext
→ Real Domain Services
→ Projection

Grounded capabilities:

* Successor Recommendation
* Knowledge Transfer Planning
* Risk Analysis

---

## Deferred To M24

Forecast and Simulation remain partially fixture-backed.

Reason:

The temporal intelligence layer is incomplete.

Missing capabilities:

* Health Snapshot Repository
* Health History Builder
* Trend Generation Pipeline
* Readiness Scoring Service

These are intelligence gaps rather than adapter wiring gaps.

---

## Outcome

PIA transitioned from:

Agent
→ Fixtures

to:

Agent
→ Real Organizational Intelligence

This is the first milestone where the reasoning agent became a genuine interface to the intelligence engine.
