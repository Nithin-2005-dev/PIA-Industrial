# Milestone 13 - Team Expertise Mapping

**Status:** Completed

## Objective

Provide repository-wide visibility into expertise distribution.

The system should answer:

* Which developers contribute the most expertise?
* Which modules are covered by each developer?
* Who are the strongest contributors across the repository?
* How is expertise distributed across the team?

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

---

## Implemented Components

### ExpertiseProfile

Repository-wide expertise profile for a developer.

**Fields**

* developer_ref
* module_count
* covered_modules
* total_expertise
* average_expertise

Provides a developer-centric view of expertise.

---

### ExpertiseMappingPolicy

Strategy abstraction for expertise mapping.

Responsibilities:

* Build developer expertise profiles
* Aggregate expertise estimates
* Support alternative mapping strategies

---

### BreadthMappingPolicy

First expertise mapping implementation.

Algorithm:

1. Group expertise estimates by developer
2. Aggregate expertise scores
3. Collect covered modules
4. Compute totals and averages
5. Rank developers by total expertise

Complexity:

O(N)

Where N is the number of expertise estimates.

---

### ContributorRanking

Represents ranked contributors.

**Fields**

* profile
* rank

---

### ExpertiseMappingService

Coordinates expertise profile generation.

Responsibilities:

* Build expertise profiles
* Rank contributors
* Return top contributors

---

## Validation

Input:

Alice

* auth.py → 80
* billing.py → 60

Bob

* auth.py → 30

Result:

Rank #1

Developer: alice

Modules: 2

Covered Modules:

* auth.py
* billing.py

Total Expertise: 140

---

Rank #2

Developer: bob

Modules: 1

Covered Modules:

* auth.py

Total Expertise: 30

---

## Outcome

PIA can now:

* Build developer expertise profiles
* Identify top contributors
* Visualize expertise distribution
* Support expertise-focused analysis

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

↓

Organizational Graph

↓

Team Expertise Mapping

The system now supports repository-wide expertise visibility.

---

## Next Milestone

### Milestone 14 - Expertise Coverage Analysis

Analyze coverage gaps, expertise concentration, and under-supported modules.
