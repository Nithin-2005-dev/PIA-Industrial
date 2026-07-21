from typing import Dict

class PromptRegistry:
    """Manages versioned prompt templates for the cognitive runtime."""
    
    _templates: Dict[str, str] = {}
    
    @classmethod
    def get(cls, name: str, version: str = "v1") -> str:
        key = f"{name}_{version}"
        return cls._templates.get(key, "")
        
    @classmethod
    def register(cls, name: str, version: str, template: str) -> None:
        key = f"{name}_{version}"
        cls._templates[key] = template

# ─── V1 Templates ───

PromptRegistry.register("system_role", "v1", "You are the PIA AI Engineering Advisor, a world-class AI agent for software repositories.")

PromptRegistry.register("planner", "v1", """
You are the Capability Planner. Your goal is to satisfy the user's intent by reasoning over the available capabilities.
You do not execute concrete tools. You output a graph of capabilities needed.

User Query: {query}
Available Capabilities:
{capabilities}

Output format:
CAPABILITY_GRAPH:
- <capability_name>
- <capability_name>

Reasoning:
<Why these capabilities are needed>
""")

PromptRegistry.register("reflection", "v1", """
Review the intermediate working memory and current findings to determine if the query can be fully answered.
If missing information is identified, you must flag `should_replan: true` and specify what is missing.
""")

PromptRegistry.register("rewriter", "v1", """
Rewrite the following deterministic engineering report into a fluent, easy-to-read executive response.
Do NOT invent facts, alter statistics, or add recommendations not present in the original report.

Deterministic Report:
{report}
""")

PromptRegistry.register("critic", "v1", """
Critique the following claims based on the evidence.
""")

