import dataclasses
from typing import List, Protocol
from .models import ExecutionState

class PromptSection(Protocol):
    def render(self, state: ExecutionState) -> str:
        ...

@dataclasses.dataclass
class PromptDocument:
    sections: List[PromptSection]

    def render(self, state: ExecutionState) -> str:
        return "\n\n".join(section.render(state) for section in self.sections)

class SystemPromptSection(PromptSection):
    def render(self, state: ExecutionState) -> str:
        return "You are an expert software architecture intelligence agent.\nYour goal is to choose the correct capabilities to fulfill the user's objective."

class ConversationHistorySection(PromptSection):
    def render(self, state: ExecutionState) -> str:
        if not state.conversation_memory.history:
            return ""
        out = "### Conversation History\n"
        for entry in state.conversation_memory.history[-3:]:
            out += f"User: {entry.query}\nSystem: {entry.response[:200]}...\n\n"
        return out

class RepositorySummarySection(PromptSection):
    def render(self, state: ExecutionState) -> str:
        summary = state.repository_memory.semantic_summary
        if not summary:
            return ""
        return f"### Repository Summary\n{summary}"

class WorkingMemorySection(PromptSection):
    def render(self, state: ExecutionState) -> str:
        out = "### Agent Memory\n"
        
        # Repository Facts/Observations
        if state.repository_memory.facts:
            out += "Facts:\n" + "\n".join(f"- {f}" for f in state.repository_memory.facts) + "\n\n"
        if state.repository_memory.observations:
            out += "Observations:\n" + "\n".join(f"- {o.tool}: {str(o.output)[:100]}" for o in state.repository_memory.observations) + "\n\n"
            
        # Agent Memory
        if state.agent_memory.goals:
            out += "Goals:\n" + "\n".join(f"- {g}" for g in state.agent_memory.goals) + "\n\n"
        if state.agent_memory.hypotheses:
            out += "Hypotheses:\n" + "\n".join(f"- {h}" for h in state.agent_memory.hypotheses) + "\n\n"
            
        return out.strip()

class ConstraintsSection(PromptSection):
    def render(self, state: ExecutionState) -> str:
        out = "### Constraints\n"
        if state.agent_memory.constraints:
            out += "\n".join(f"- {c}" for c in state.agent_memory.constraints)
        else:
            out += "None."
        return out

class AvailableToolsSection(PromptSection):
    def __init__(self, tools_description: str):
        self.tools_description = tools_description

    def render(self, state: ExecutionState) -> str:
        return f"### Available Capabilities\n{self.tools_description}"

class GoalSection(PromptSection):
    def render(self, state: ExecutionState) -> str:
        return f"### Current Goal\n{state.goal.query}"

class PromptBuilder:
    def build_planner_prompt(self, state: ExecutionState, tools_description: str) -> str:
        doc = PromptDocument(sections=[
            SystemPromptSection(),
            RepositorySummarySection(),
            ConversationHistorySection(),
            WorkingMemorySection(),
            ConstraintsSection(),
            AvailableToolsSection(tools_description),
            GoalSection()
        ])
        
        prompt = doc.render(state)
        
        # Add instruction
        prompt += "\n\nOutput ONLY JSON array of required capabilities (if you need any), or an empty array if you have enough information to answer."
        prompt += """
Format:
[
  {
    "name": "forecast",
    "confidence": 0.9,
    "reason": "Needs temporal extrapolation"
  }
]
"""
        return prompt
