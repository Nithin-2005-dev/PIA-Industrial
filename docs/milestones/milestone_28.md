# Milestone 28 — Organization Intelligence Layer

## Goal

Prior milestones focused on module-level intelligence.

M28 introduces organization-level intelligence by aggregating existing intelligence services into executive-facing views.

The objective is to answer questions such as:

* What is our biggest organizational risk?
* How healthy is the organization?
* Which modules have successor gaps?
* Where should we invest knowledge transfer?
* What should leadership focus on?

---

## Motivation

Before M28, the system exposed:

```text
Coverage
Concentration
Bus Factor
Health
Forecast
Future Risk
Successor
Readiness
Transfer
Simulation
```

but all intelligence was module-centric.

Questions required explicit module references.

Examples:

```text
Why is auth.py risky?
Who owns payments.py?
Who should replace Alice?
```

There was no organization-wide aggregation layer.

---

## M28.1 — OrganizationRiskService

Created:

```text
app/organization/organization_risk.py
app/organization/organization_risk_service.py
```

Purpose:

```text
Cross-module risk ranking
```

Pipeline:

```text
Health History
        ↓
Trend
        ↓
Forecast
        ↓
Future Risk
        ↓
Organization Risk Ranking
```

Output:

```text
#1 payments.py
#2 auth.py
#3 analytics.py
```

---

## M28.2 — OrganizationHealthService

Created:

```text
app/organization/organization_health.py
app/organization/organization_health_service.py
```

Purpose:

```text
Aggregate organizational health
```

Metrics:

* Average Health
* Best Health
* Worst Health
* Healthy Modules
* Warning Modules
* Critical Modules

Example:

```text
Average Health: 31.50
Best Health: 41.00
Worst Health: 22.00
```

---

## M28.3 — OrganizationReadinessService

Created:

```text
app/organization/organization_readiness.py
app/organization/organization_readiness_service.py
```

Purpose:

```text
Identify successor gaps
```

Pipeline:

```text
ReadinessService
        ↓
Best Successor
        ↓
Organization Ranking
```

Example:

```text
#1 payments.py
Readiness: 0.21

#2 auth.py
Readiness: 0.24
```

Lower readiness indicates higher organizational succession risk.

---

## M28.4 — OrganizationTransferService

Created:

```text
app/organization/organization_transfer.py
app/organization/organization_transfer_service.py
```

Purpose:

```text
Rank highest-value transfer opportunities
```

Pipeline:

```text
Ownership
Successors
Concentration
        ↓
Transfer Plans
        ↓
Organization Ranking
```

Example:

```text
#1 auth.py
Mentor: alice
Learner: bob
Priority: 115.00
```

---

## M28.5 — OrganizationDashboardService

Created:

```text
app/organization/organization_dashboard.py
app/organization/organization_dashboard_service.py
```

Purpose:

```text
Executive summary view
```

Combines:

```text
OrganizationHealthService
OrganizationRiskService
OrganizationReadinessService
OrganizationTransferService
```

Output:

```text
Average Health: 31.50

Top Risk:
payments.py

Weakest Readiness:
payments.py

Top Transfer:
payments.py
```

---

## Architecture After M28

```text
Expertise
        ↓
Ownership
        ↓
Coverage
Concentration
Bus Factor
        ↓
Health
        ↓
History
        ↓
Trend
        ↓
Forecast
        ↓
Future Risk

Ownership
        ↓
Successor
        ↓
Readiness

Ownership
Successor
Concentration
        ↓
Transfer
```

Organization Layer:

```text
Risk Ranking
Health Summary
Readiness Ranking
Transfer Ranking
Dashboard
```

---

## Result

M28 transforms PIA from module intelligence into organization intelligence.

The system can now reason about:

* organizational risk
* organizational health
* succession readiness
* knowledge transfer priorities
* executive-level focus areas

without requiring a specific module as input.
