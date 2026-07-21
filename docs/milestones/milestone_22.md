# Milestone 22 - Organizational Reasoning Agent

Status: Completed

## Objective

Provide a single natural-language entry point for organizational intelligence.

Questions answered:

* Which modules are risky?
* Which modules are deteriorating?
* How can we improve a module?
* What happens if a developer leaves?

---

## Architecture

Question

↓

Intent Classification

↓

Tool Routing

↓

Tool Execution

↓

Adapter Layer

↓

Organizational Intelligence

↓

Answer

---

## Implemented Components

### QuestionIntent

Represents organizational question categories.

Supported intents:

* RISK
* FORECAST
* INTERVENTION
* SIMULATION

---

### IntentClassifier

Detects user intent from natural language questions.

Responsibilities:

* Question understanding
* Intent detection
* Capability selection

---

### ToolRoute

Maps intents to organizational capabilities.

Routes:

* Risk Analysis
* Forecast Analysis
* Intervention Planning
* Simulation Engine

---

### ToolExecutor

Coordinates adapter execution.

Responsibilities:

* Route resolution
* Capability invocation
* Response construction

---

### AgentResponse

Standardized agent response object.

Fields:

* intent
* route
* summary

---

### Adapter Layer

#### RiskAdapter

Provides organizational risk intelligence.

Uses:

* Coverage
* Concentration
* Health

---

#### ForecastAdapter

Provides predictive intelligence.

Uses:

* Forecast
* Future Risk

---

#### InterventionAdapter

Provides action intelligence.

Uses:

* Coverage Analysis
* Concentration Analysis
* Forecast Severity
* Intervention Planner

---

#### SimulationAdapter

Provides scenario intelligence.

Uses:

* Ownership
* Health
* Successor Readiness
* Simulation Engine

---

## Validation

### Risk Question

Question:

Which modules are risky?

Response:

Coverage: 10

Concentration: 0.98

Health: 40

Level: CRITICAL

---

### Forecast Question

Question:

Which modules are deteriorating?

Response:

Current Health: 40

Predicted Health: 10

Risk Score: 30

---

### Intervention Question

Question:

How can we improve payments.py?

Response:

1. Immediate knowledge transfer (+22.50)

2. Reduce knowledge concentration (+19.60)

3. Train additional experts (+7.50)

Total Expected Gain: 49.60

---

### Simulation Question

Question:

What happens if Alice leaves?

Response:

Health Before: 80

Health After: 56

Knowledge Loss: 0.30

Impact: -24

Severity: MODERATE

---

## Outcome

PIA can now:

* Understand organizational questions
* Select appropriate intelligence capabilities
* Execute reasoning workflows
* Produce organizational answers

---

## Architectural Outcome

Before M22:

User

↓

Direct Service Invocation

↓

Result

---

After M22:

Question

↓

Agent

↓

Organizational Intelligence

↓

Answer

---

## Key Insight

The value of organizational intelligence increases significantly when users interact through questions rather than individual services.

M22 transforms PIA from a collection of capabilities into a unified reasoning system.

---

## Next Milestone

Stress-test the agent using realistic engineering-management questions before defining M23.
