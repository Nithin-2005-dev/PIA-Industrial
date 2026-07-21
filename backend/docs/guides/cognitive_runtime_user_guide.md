# Cognitive Runtime User Guide

Welcome to the official developer guide for the **Cognitive Intelligence Layer** in PIA. This guide explains how the Cognitive Runtime works, how to use it, and how to extend it.

## 1. Complete End-to-End Example

Here is a complete, runnable example of executing the deterministic pipeline and invoking the Cognitive Runtime.

```python
import os
from app.platform.runtime import PlatformRuntime
from app.kernel.runtime import CognitiveRuntime
from app.kernel.provider import OpenAIProvider

# 1. Run deterministic pipeline (The Source of Truth)
platform = PlatformRuntime.create()
platform.register_default_modules()

result = platform.run(
    repository="facebook/react",
    commits=100,
)

# 2. Create provider
provider = OpenAIProvider(
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-5"
)

# 3. Create cognitive runtime
runtime = CognitiveRuntime(provider=provider)

# 4. Create conversation session
session = runtime.create_session()

# 5. Ask question
response = runtime.answer(
    platform_result=result,
    question="Why is frontend quality decreasing?",
    session=session,
)

print(response.executive_response.executive_summary)
```

## 2. How to Chat with the System

`CognitiveSession` is crucial for multi-turn conversations. It preserves history so follow-up questions understand context.

```python
session = runtime.create_session()

# Turn 1
resp1 = runtime.answer(platform_result, "Summarize repository health.", session)
print("AI:", resp1.executive_response.executive_summary)

# Turn 2
resp2 = runtime.answer(platform_result, "Why is that?", session)
print("AI:", resp2.executive_response.executive_summary)

# Turn 3
resp3 = runtime.answer(platform_result, "What should we prioritize?", session)
print("AI:", resp3.executive_response.actionable_recommendations)
```

## 3. High-Level Architecture

* **PlatformRuntime**: The deterministic engine ("What is true?").
* **CognitiveRuntime**: The on-demand entry point for LLMs ("What does the user want to know?").
* **CapabilityRegistry**: A registry mapping capabilities to deterministic tools.
* **PlanningEngine**: Acts as a retrieval planner, mapping user intent to specific `ToolSpecification`s.
* **EvidenceRetriever**: Extracts summarized, safe-for-LLM `PromptArtifact`s.
* **ContextBuilder & PromptComposer**: Bundles artifacts and history, enforcing token budgets.
* **ReasoningOrchestrator**: The core loop orchestrating the LLM, Critic, and Verifier.
* **CriticEngine & EvidenceVerificationEngine**: Maps every generated claim to canonical evidence, stripping hallucinations.

## 4. Supported Questions

The `PlanningEngine` maps natural language to capabilities:

| Question                  | Tools Used            |
| ------------------------- | --------------------- |
| Repository summary        | Executive             |
| Why is health decreasing? | Organization + Causal |
| Forecast next month       | Forecast              |
| Compare scenarios         | Simulation            |
| Best intervention         | Optimization          |
| Explain recommendation    | Decision + Causal     |
| Show evidence             | Evidence              |
| Explain knowledge graph   | Knowledge Graph       |

## 5. Prompt and Retrieval Inspection

When building or debugging, you can inspect exactly what the planner chose, what artifacts were retrieved, and the raw prompt sent to the LLM.

```python
response = runtime.answer(platform_result, "Why is bus factor decreasing?")

# Inspect Planner Selection
print("Tools Selected:", response.plan.selected_tools)

# Inspect Retrieved Artifacts
for artifact in response.prompt_context.artifacts:
    print(artifact.id, artifact.confidence)

# Inspect the Raw Prompt
final_prompt = runtime.composer.compose(response.prompt_context)
print(final_prompt)

# Inspect Verification (Hallucination removal)
print("Dropped claims:", response.answer.verification.dropped_claims)
for critique in response.answer.verification.critiques:
    print(critique.claim, critique.is_supported)
```

## 6. Hallucination Prevention

PIA strictly prohibits LLM hallucinations. The `CriticEngine` evaluates generated text. The `EvidenceVerificationEngine` resolves these critiques. If an LLM hallucinates an unsupported claim (e.g. "React has 57 maintainers"), the Verifier redacts it to `[UNVERIFIED CLAIM REMOVED]`.

## 7. Error Handling

You should anticipate and handle several failure scenarios:

- **Missing API key**: Provider instantiation will raise `ValueError` or a provider-specific auth error. Catch this or fallback to `MockLLMProvider`.
- **Timeout**: Network failures to LLMs happen. Wrap `runtime.answer` in a standard retry/timeout block.
- **Token limit**: The `PromptComposer` truncates evidence automatically, but if your conversation history exceeds the limit, it will drop older context.
- **Empty PlatformResult**: If `PlatformRuntime` failed, `PlatformResult` is invalid. Always check `if not platform_result.errors:` before invoking the cognitive layer.
- **Verification failure**: If the LLM produces a completely hallucinated response, all claims may be stripped, returning a heavily redacted output.

## 8. Performance Characteristics

It is critical to understand the separation of concerns:

- **PlatformRuntime**: Highly computationally expensive. Expect **seconds to minutes** depending on repository size.
- **CognitiveRuntime**: Instantaneous locally, constrained purely by **LLM network latency (milliseconds/seconds)**.

You **do not** need to rerun the deterministic pipeline for every question. Run `PlatformRuntime` once per session/commit, and interact with `CognitiveRuntime` indefinitely over that snapshot.

## 9. Future Roadmap

The Cognitive Runtime in M57 provides the foundation for autonomous intelligence.

* **Current (M57)**: Planner -> Retriever -> Verifier
* **Future (M58)**: Semantic Memory (Persistent retrieval across sessions)
* **Future (M59)**: Reflection (Self-correcting semantic loops)
* **Future (M60)**: Autonomous Tool Use (Dynamic LLM tool execution)
* **Future (M61)**: Multi-Repository Intelligence
