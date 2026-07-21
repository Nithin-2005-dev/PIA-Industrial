# Milestone 8 - Ownership Detection

Status: Completed

## Objective

Infer ownership relationships between developers and modules using expertise estimates.

The system should answer:

Who owns this file?

Ownership should emerge from accumulated expertise rather than being explicitly stored.

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

---

## Implemented Components

### OwnershipEstimate

Represents an ownership relationship between a developer and a module.

Fields:

* owner_ref
* module_ref
* ownership_percentage
* effective_score
* ownership_level

---

### OwnershipLevel

Introduced ownership classifications.

Values:

* PRIMARY
* SECONDARY
* CONTRIBUTOR

Rules:

* ownership ≥ 60% → PRIMARY
* ownership ≥ 20% → SECONDARY
* otherwise → CONTRIBUTOR

---

### OwnershipPolicy

Strategy abstraction for deriving ownership from expertise.

Responsibilities:

* Transform expertise into ownership relationships
* Remain independent from orchestration logic

---

### ExpertiseOwnershipPolicy

First ownership implementation.

Formula:

ownership_percentage =

developer_effective_score

/

total_module_effective_score

The resulting ownership distribution is normalized across all experts of a module.

---

### OwnershipService

Coordinates ownership generation.

Responsibilities:

* Retrieve module experts through the query layer
* Delegate ownership computation to an ownership policy
* Return ownership estimates

---

## Validation

Module:

packages/react-devtools-facade/src/DevToolsFacade.js

Result:

Developer:

hoxyq

Ownership:

100.00%

Level:

PRIMARY

Effective Score:

4.80

---

## Outcome

PIA can now infer:

* Current owner
* Ownership distribution
* Primary maintainers
* Secondary maintainers
* Contributors

Ownership is now derived knowledge rather than stored metadata.

---

## Architectural Outcome

The system now supports:

Activity
↓
Knowledge
↓
Time-Aware Knowledge
↓
Ownership

This establishes the foundation for organizational risk analysis.

---

## Next Milestone

Milestone 9 - Bus Factor Analysis

Determine how resilient a module is to developer loss using ownership distributions.
