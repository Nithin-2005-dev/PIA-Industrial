# Milestone 15 - Expertise Concentration Analysis

**Status:** Completed

## Objective

Identify modules where expertise is heavily concentrated in a small number of contributors.

The system should answer:

* Who controls the majority of knowledge?
* Which modules are vulnerable to contributor loss?
* Is expertise evenly distributed?
* Which modules hide concentration risk despite reasonable coverage?

---

## Architecture

GitHub

↓

Events

↓

Evidence

↓

Expertise

↓

Ownership

↓

Risk

↓

Knowledge Risk

↓

Successor Planning

↓

Organizational Graph

↓

Team Expertise Mapping

↓

Expertise Coverage Analysis

↓

Expertise Concentration Analysis

---

## Implemented Components

### ConcentrationReport

Represents expertise concentration for a module.

**Fields**

* module_ref
* expert_count
* concentration_score
* concentration_level

---

### ConcentrationPolicy

Strategy abstraction for concentration analysis.

Responsibilities:

* Analyze expertise distribution
* Produce concentration reports
* Support future concentration algorithms

---

### ExpertiseConcentrationPolicy

First concentration analysis implementation.

Algorithm:

1. Group expertise estimates by module
2. Compute total expertise
3. Find strongest expert
4. Calculate concentration score
5. Assign concentration level

Formula:

concentration_score =
largest_expert_score / total_expertise

Concentration Levels:

* LOW ≤ 0.40
* MODERATE ≤ 0.70
* HIGH > 0.70

---

### ConcentrationRisk

Represents a ranked concentration risk.

**Fields**

* report
* rank

---

### ConcentrationService

Coordinates concentration analysis.

Responsibilities:

* Analyze concentration
* Rank concentration risks
* Return highest-risk modules

---

## Validation

### Balanced Knowledge Distribution

auth.py

Alice → 80

Bob → 80

Charlie → 80

Total Expertise = 240

Largest Expert = 80

Concentration Score:

80 / 240 = 0.33

Result:

LOW

---

### Dangerous Knowledge Concentration

payments.py

David → 100

Emma → 1

Frank → 1

Total Expertise = 102

Largest Expert = 100

Concentration Score:

100 / 102 = 0.98

Result:

HIGH

---

### Concentration Risk Ranking

Rank #1

payments.py

Score: 0.98

Level: HIGH

---

Rank #2

auth.py

Score: 0.33

Level: LOW

---

## Outcome

PIA can now:

* Detect knowledge concentration
* Identify hidden organizational risks
* Rank concentration vulnerabilities
* Distinguish coverage from distribution

---

## Architectural Outcome

Expertise

↓

Coverage

↓

Concentration

The system now reasons about both the quantity and distribution of knowledge.

---

## Limitations

Current concentration analysis only considers the strongest contributor.

Future improvements may use:

* Shannon Entropy
* Gini Coefficient
* Herfindahl-Hirschman Index
* Ownership-weighted concentration

to provide more accurate measurements.

---

## Next Milestone

### Milestone 16 - Knowledge Transfer Planning

Recommend actions for reducing knowledge concentration and improving organizational resilience.
