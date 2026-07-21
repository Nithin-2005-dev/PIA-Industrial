from typing import Any, List
from .models import PromptArtifact
from .registry import CapabilityRegistry


class ToolExecutionResult:
    """Raw data returned by a tool."""
    def __init__(self, tool_name: str, data: Any):
        self.tool_name = tool_name
        self.data = data


class ToolSelector:
    """Selects and maps requested tool names to actual capability fetchers."""
    
    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry

    def select(self, tool_names: List[str]) -> List[str]:
        """Validates that the requested tools exist in the registry."""
        selected = []
        for name in tool_names:
            tool_name = name.strip("[]'\" ")
            if self.registry.get(tool_name):
                selected.append(tool_name)
        return selected

    def execute(self, tool_name: str, platform_result: Any) -> ToolExecutionResult:
        """Fetches the corresponding context from the deterministic platform result."""
        # Simple extraction based on standard platform context attributes
        if tool_name == "forecast":
            return ToolExecutionResult(tool_name, getattr(platform_result, "forecast_context", None))
        elif tool_name == "simulation":
            return ToolExecutionResult(tool_name, getattr(platform_result, "simulation_context", None))
        elif tool_name == "organization":
            return ToolExecutionResult(tool_name, getattr(platform_result, "org_intelligence", None))
        elif tool_name == "causal":
            return ToolExecutionResult(tool_name, getattr(platform_result, "causal_context", None))
        elif tool_name == "knowledge_graph":
            return ToolExecutionResult(tool_name, getattr(platform_result, "knowledge_graph", None))
            
        return ToolExecutionResult(tool_name, None)
