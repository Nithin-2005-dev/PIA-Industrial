# Milestone 11 - Successor Recommendation

Status: Completed

## Objective

Recommend potential future owners for a module when the current owner becomes unavailable.

The system should answer:

* Who should take over this module?
* Who is the strongest successor candidate?
* Which contributors are closest to ownership readiness?

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

Successor Recommendation

---

## Implemented Components

### SuccessorCandidate

Represents a recommended future owner.

Fields:

* developer_ref
* module_ref
* score
* rank

---

### SuccessorPolicy

Strategy abstraction for successor recommendation.

Responsibilities:

* Evaluate ownership distributions
* Select successor candidates
* Remain independent from orchestration logic

---

### ExpertiseSuccessorPolicy

First successor recommendation implementation.

Algorithm:

1. Sort ownership distribution by ownership percentage
2. Remove the strongest current owner
3. Recommend remaining contributors
4. Rank recommendations

This design remains independent from ownership-level semantics and works with future ownership policies.

---

### SuccessorService

Coordinates successor planning.

Responsibilities:

* Retrieve ownership information
* Delegate recommendation generation to a policy
* Return ranked successor candidates

---

## Validation

Module:

auth.py

Ownership Distribution:

Alice → 70%

Bob → 20%

Charlie → 10%

Result:

Rank #1

Bob

Score: 20

---

Rank #2

Charlie

Score: 10

---

## Outcome

PIA can now:

* Recommend successor candidates
* Support ownership continuity planning
* Reduce knowledge concentration risk
* Assist succession planning

The system now provides mitigation guidance rather than only reporting risk.

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

Knowledge Risk

↓

Successor Planning

This establishes the first prescriptive intelligence capability within PIA.

---

## Next Milestone

Milestone 12 - Organizational Graph

Model relationships between developers, modules, ownership, expertise, and risk across the entire repository.
