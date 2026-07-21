# PIA Research Notebook

# Volume I — Foundations

## Chapter 5 — RAM-2.2: Knowledge versus Capability

**Version:** 1.0 (Research Draft)

**Status:** Frozen after Review

---

# 1. Introduction

The previous chapter concluded that organizational knowledge is a multidimensional latent variable.

However, an important question remains unanswered.

> **Does possessing knowledge imply the ability to perform engineering tasks?**

Most software engineering research implicitly assumes the answer is yes.

PIA challenges this assumption.

This chapter investigates whether **Knowledge** and **Capability** represent the same latent variable or two fundamentally different organizational properties.

---

# 2. Motivation

Current expertise estimation systems generally make the following assumption:

```text
Activity
      ↓
Knowledge
      ↓
Capability
```

This chain implies that more knowledge automatically produces greater capability.

Although intuitive, this assumption fails under many real-world scenarios.

Understanding these failures is essential for constructing an accurate model of organizational intelligence.

---

# 3. Research Question

The central question of this chapter is

> **Can software engineering knowledge and software engineering capability be represented by the same latent variable?**

If the answer is no,

then PIA must estimate multiple interacting hidden variables rather than a single expertise score.

---

# 4. Defining Knowledge

Knowledge represents understanding.

It answers questions such as

* Why does the system behave this way?
* How is the architecture organized?
* What assumptions were made?
* Why was this algorithm selected?

Knowledge concerns explanation rather than execution.

Knowledge is therefore cognitive.

---

# 5. Defining Capability

Capability represents execution.

It answers questions such as

* Can this developer implement a feature?
* Can they fix a production issue?
* Can they review a pull request?
* Can they optimize performance?

Capability concerns successful action rather than understanding.

Capability is therefore operational.

---

# 6. Thought Experiment I — The Original Architect

Developer A designed the architecture five years ago.

Since then,

they have not modified the project.

Questions

Does Developer A still understand the architecture?

Most experts answer

Yes.

Can Developer A immediately implement complex production fixes?

Not necessarily.

Conclusion

Knowledge remains.

Capability may decline.

Knowledge and capability evolve differently.

---

# 7. Thought Experiment II — The Production Maintainer

Developer B maintains production every day.

They resolve incidents rapidly.

However,

they were not involved in the original design.

Questions

Can Developer B resolve failures?

Yes.

Can Developer B explain every architectural decision?

Possibly not.

Conclusion

Capability exceeds architectural knowledge.

Again,

the two variables differ.

---

# 8. Thought Experiment III — The Reviewer

Developer C reviews nearly every pull request.

They rarely commit code.

Questions

Do they understand the system?

Likely yes.

Do they possess strong implementation capability?

Unknown.

Review activity develops evaluation ability rather than implementation speed.

---

# 9. Thought Experiment IV — Documentation Specialist

Developer D maintains technical documentation.

They explain architecture exceptionally well.

However,

they rarely write production code.

Questions

Do they possess knowledge?

Yes.

Do they possess high implementation capability?

Not necessarily.

Documentation primarily transfers knowledge rather than implementation skill.

---

# 10. Comparative Analysis

| Property            | Knowledge                            | Capability                    |
| ------------------- | ------------------------------------ | ----------------------------- |
| Represents          | Understanding                        | Execution                     |
| Observable          | No                                   | No                            |
| Directly Measurable | No                                   | No                            |
| Evolves             | Slowly                               | Faster                        |
| Can Decay           | Slowly                               | Rapidly                       |
| Transferable        | High                                 | Moderate                      |
| Improved By         | Learning                             | Practice                      |
| Primary Evidence    | Architecture, Reviews, Documentation | Coding, Debugging, Operations |

This comparison demonstrates that the two concepts possess fundamentally different characteristics.

---

# 11. Temporal Behaviour

Knowledge and capability evolve differently through time.

Knowledge tends to accumulate gradually.

It decays slowly through forgetting.

Capability improves through repeated execution.

It declines rapidly through inactivity.

Therefore,

a single decay function cannot accurately represent both variables.

This observation has major implications for future inference algorithms.

---

# 12. Relationship Between Knowledge and Capability

Although distinct,

knowledge and capability influence one another.

Knowledge supports capability.

Capability reinforces knowledge through repeated application.

However,

neither completely determines the other.

Therefore,

they should be modeled as interacting latent variables rather than independent quantities.

---

# 13. Proposed Human State

This chapter proposes the following representation.

Human State

H

consists of

Knowledge

K

and

Capability

C

Therefore

H = (K, C)

This representation separates understanding from execution while allowing both variables to interact during inference.

---

# 14. Implications for PIA

Current Systems

```text
Commit
      ↓
Expertise Score
```

Future PIA

```text
Observations
        ↓
Knowledge Estimation
        ↓
Capability Estimation
        ↓
Decision Functions
```

Ownership,

successor recommendation,

organizational health,

and forecasting

will now depend upon multiple latent variables rather than a single heuristic score.

---

# 15. Research Contributions

RAM-2.2 establishes the following principles.

### Principle 1

Knowledge and capability are distinct latent variables.

---

### Principle 2

Knowledge does not imply capability.

---

### Principle 3

Capability does not imply complete knowledge.

---

### Principle 4

Knowledge and capability evolve according to different temporal dynamics.

---

### Principle 5

Future inference algorithms should estimate both variables simultaneously.

---

# 16. Remaining Challenge

Even after separating knowledge and capability,

one important question remains.

How certain are these estimates?

Two developers may possess identical estimated knowledge,

yet one estimate may be based upon hundreds of observations while another is based upon only two.

The estimates should therefore not be trusted equally.

This introduces the concept of estimation uncertainty.

---

# 17. Transition to RAM-2.3

The next chapter introduces the third latent variable required by PIA.

> **Confidence**

Confidence measures the certainty of the inference process rather than the ability of the developer.

Separating uncertainty from organizational state enables principled probabilistic reasoning and forms the foundation for Bayesian state estimation.

---

# Chapter Summary

RAM-2.2 demonstrates that organizational intelligence cannot be represented by knowledge alone.

Knowledge explains understanding.

Capability explains execution.

Although closely related,

they represent different aspects of human expertise,

evolve differently through time,

and require independent estimation.

This separation forms one of the core theoretical contributions of the PIA framework.
