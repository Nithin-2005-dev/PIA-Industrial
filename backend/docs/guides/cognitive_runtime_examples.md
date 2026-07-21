# Cognitive Runtime Examples

This document provides code-first, practical examples of integrating and querying the Cognitive Runtime.

## 1. Complete End-to-End Example

```python
import os
from app.platform.runtime import PlatformRuntime
from app.kernel.runtime import CognitiveRuntime
from app.kernel.provider import OpenAIProvider

# 1. Run deterministic pipeline
platform = PlatformRuntime.create()
platform.register_default_modules()

result = platform.run(
    repository="facebook/react",
    commits=100,
)

# 2. Create provider
provider = OpenAIProvider(api_key=os.environ.get("OPENAI_API_KEY"), model="gpt-5")

# 3. Create cognitive runtime
runtime = CognitiveRuntime(provider=provider)

# 4. Create conversation
session = runtime.create_session()

# 5. Ask question
response = runtime.answer(
    platform_result=result,
    question="Why is frontend quality decreasing?",
    session=session,
)

print(response.executive_response.executive_summary)
```

## 2. Multi-turn Chat

```python
session = runtime.create_session()

resp1 = runtime.answer(result, "Summarize repository health.", session)
print("AI:", resp1.executive_response.executive_summary)

resp2 = runtime.answer(result, "Why is that?", session)
print("AI:", resp2.executive_response.executive_summary)

resp3 = runtime.answer(result, "What should we prioritize?", session)
print("AI:", resp3.executive_response.actionable_recommendations)
```

## 3. Prompt and Retrieval Inspection

Debug what the LLM is actually seeing:

```python
response = runtime.answer(result, "Why is bus factor decreasing?", session)

# 1. Tools Selected
print("Planner Selected:", response.plan.selected_tools)

# 2. Retrieved Artifacts
for artifact in response.prompt_context.artifacts:
    print(f"[{artifact.confidence}] {artifact.id}: {artifact.summary}")

# 3. Raw Prompt (Optional - via composer)
final_prompt = runtime.composer.compose(response.prompt_context)
print(final_prompt)

# 4. Verifier Action
print("Dropped claims:", response.answer.verification.dropped_claims)
for critique in response.answer.verification.critiques:
    print(f"{critique.claim}: Supported={critique.is_supported}")
```

## 4. Error Handling Boilerplate

```python
try:
    if result.errors:
        raise ValueError("PlatformRuntime failed to produce a valid context.")
        
    response = runtime.answer(result, "Is the repository healthy?", session)
    
except ValueError as e:
    print("Invalid Setup:", e)
except ConnectionError as e:
    print("LLM Provider unreachable. Falling back to cache or mock.")
except Exception as e:
    print("Unexpected Verification Failure:", e)
```
