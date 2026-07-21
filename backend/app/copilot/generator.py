"""LLM Generator for Industrial Intelligence.

Provides a clean interface for LLM generation. For the hackathon,
this includes a mock generator that formats the retrieved evidence
into a simulated LLM response, allowing end-to-end testing without
requiring API keys.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMGenerator(ABC):
    """Abstract interface for LLM text generation."""

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a response based on prompts."""
        ...


class MockLLMGenerator(LLMGenerator):
    """A mock generator for testing and demonstration.

    Simulates an LLM response by extracting facts from the
    provided evidence context and formatting them with citations.
    """

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        # Extract evidence context from system prompt
        context_start = system_prompt.find("--- EVIDENCE CONTEXT ---")
        context_end = system_prompt.find("--- END EVIDENCE CONTEXT ---")
        
        if context_start == -1 or context_end == -1:
            return "Error: Could not find evidence context."

        context = system_prompt[context_start:context_end]
        
        # Parse citations and content
        lines = context.split("\n")
        citations: dict[str, str] = {}
        current_citation = ""
        
        for line in lines:
            if line.startswith("Citation: "):
                current_citation = line.replace("Citation: ", "").strip()
            elif line.startswith("Content: ") and current_citation:
                content = line.replace("Content: ", "").strip()
                # For the mock, just take the first sentence of the content
                first_sentence = content.split(". ")[0]
                citations[current_citation] = first_sentence
                current_citation = ""

        if not citations:
            return "I cannot find evidence to answer this question."

        # Build a simulated response
        response = [
            "Based on the provided evidence, here is the analysis:\n"
        ]
        
        for tag, fact in citations.items():
            response.append(f"- {fact} {tag}")
            
        return "\n".join(response)
