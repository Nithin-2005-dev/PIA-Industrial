"""Industrial Knowledge Copilot Orchestrator.

Ties together the router, retriever, ranker, and generator
to answer user queries using grounded industrial intelligence.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from app.copilot.generator import LLMGenerator, MockLLMGenerator
from app.copilot.prompts import (
    HISTORY_PROMPT,
    STATUS_PROMPT,
    SYSTEM_PROMPT_TEMPLATE,
    TROUBLESHOOTING_PROMPT,
)
from app.copilot.router import QueryIntent, QueryRouter
from app.knowledge.retrieval.evidence_ranker import EvidenceRanker, RankedEvidence
from app.knowledge.retrieval.hybrid_retriever import HybridRetriever

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CopilotResponse:
    """The final response from the copilot."""
    answer: str
    intent: str
    evidence: tuple[RankedEvidence, ...]
    metadata: dict[str, Any] = field(default_factory=dict)


class IndustrialCopilot:
    """The main entry point for asking industrial questions."""

    def __init__(
        self,
        retriever: HybridRetriever,
        generator: LLMGenerator | None = None,
    ) -> None:
        self._router = QueryRouter()
        self._retriever = retriever
        self._ranker = EvidenceRanker()
        self._generator = generator or MockLLMGenerator()

    def ask(self, query: str) -> CopilotResponse:
        """Answer a user query using grounded evidence."""
        logger.info(f"Copilot received query: '{query}'")

        # 1. Route Intent
        intent = self._router.route_query(query)
        logger.info(f"Classified intent: {intent.value}")

        # 2. Retrieve Evidence
        context = self._retriever.retrieve(query)

        # 3. Rank Evidence
        ranked_evidence = self._ranker.rank_and_format(context)
        evidence_context_str = self._ranker.build_prompt_context(ranked_evidence)

        # 4. Select Intent Prompt
        intent_prompt = ""
        if intent == QueryIntent.TROUBLESHOOTING:
            intent_prompt = TROUBLESHOOTING_PROMPT
        elif intent == QueryIntent.ASSET_STATUS:
            intent_prompt = STATUS_PROMPT
        elif intent == QueryIntent.MAINTENANCE_HISTORY:
            intent_prompt = HISTORY_PROMPT

        # 5. Build Final Prompt
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            evidence_context=evidence_context_str
        )
        
        user_prompt = f"{intent_prompt}\n\nUser Question: {query}"

        # 6. Generate Response
        if not ranked_evidence:
            answer = "I cannot find evidence to answer this question."
        else:
            answer = self._generator.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

        # 7. Verify Citations (Basic post-processing check)
        # Ensure the LLM didn't invent citation tags
        answer = self._verify_citations(answer, ranked_evidence)

        return CopilotResponse(
            answer=answer,
            intent=intent.value,
            evidence=tuple(ranked_evidence),
            metadata={
                "extracted_entities": context.metadata.get("extracted_entities", 0),
                "semantic_matches": context.metadata.get("semantic_matches", 0),
                "neighborhoods": context.metadata.get("neighborhoods_found", 0),
            },
        )

    def _verify_citations(
        self,
        answer: str,
        evidence: list[RankedEvidence],
    ) -> str:
        """Ensure all citation tags in the answer actually exist in evidence."""
        valid_tags = {e.citation_tag for e in evidence}
        
        # Simple verification: warn if we see a tag like [3] but we only gave [1], [2]
        import re
        used_tags = set(re.findall(r'\[\d+\]', answer))
        
        invalid_tags = used_tags - valid_tags
        if invalid_tags:
            logger.warning(f"LLM hallucinated citations: {invalid_tags}")
            # For strict mode, we could strip them, but for now just log it
            
        return answer
