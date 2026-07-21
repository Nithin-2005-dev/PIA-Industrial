# Milestone 12 - Organizational Graph

**Status:** Completed

## Objective

Unify organizational knowledge into a graph representation.

The system should answer:

* How are developers connected to modules?
* How are risks connected to ownership?
* How are successor recommendations connected to ownership?
* Can organizational knowledge be traversed as a graph?

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

---

## Implemented Components

### GraphNode

Generic graph node representation.

**Fields**

* id
* type

**Examples**

* Developer
* Module
* Risk

---

### GraphEdge

Directed relationship between nodes.

**Fields**

* source_id
* target_id
* relationship
* weight

**Examples**

* OWNS
* RISK
* SUCCESSOR

---

### OrganizationalGraph

Container for graph structures.

**Fields**

* nodes
* edges

**Responsibilities**

* Store organizational relationships
* Serve as graph query foundation

---

### GraphBuilder

Abstract strategy for graph construction.

**Responsibilities**

* Convert domain knowledge into graph structures
* Allow future graph construction approaches

---

### PIAGraphBuilder

First graph construction implementation.

Transforms:

* OwnershipEstimate
* KnowledgeRisk
* SuccessorCandidate

Into:

* GraphNode
* GraphEdge

**Relationships Produced**

* Developer → OWNS → Module
* Module → RISK → RiskNode
* Developer → SUCCESSOR → Module

---

### GraphService

Graph traversal layer.

**Capabilities**

* outgoing(node_id)
* incoming(node_id)
* neighbors(node_id)
* find_by_relationship(type)

Provides repository-wide relationship queries.

---

## Validation

### Graph Domain

Result:

```text
Nodes: 2
Edges: 1

alice --EXPERTISE--> auth.py
```

---

### Organizational Graph Build

Result:

```text
Nodes: 4
Edges: 3

alice --OWNS--> auth.py

auth.py --RISK--> risk:auth.py

bob --SUCCESSOR--> auth.py
```

---

### Graph Queries

Owners:

```text
alice
```

Successors:

```text
bob
```

Risks:

```text
risk:auth.py
```

---

## Outcome

PIA can now:

* Represent organizational knowledge as a graph
* Traverse relationships
* Connect ownership, risk, and succession
* Support graph-based reasoning

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

This creates the foundation for future organization-level intelligence.

---

## Next Milestone

### Milestone 13 - Team Expertise Mapping

Analyze expertise distribution across developers and modules using graph relationships.
