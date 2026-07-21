"""Evidence Ranker and Citation Verifier.

Ranks the retrieved context based on relevance, confidence,
and provenance, preparing it for LLM generation.
Ensures that all provided evidence is traceable.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from app.knowledge.retrieval.hybrid_retriever import RetrievedContext
from app.knowledge.retrieval.vector_store import SearchResult

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RankedEvidence:
    """A piece of ranked evidence with formatted citation."""
    content: str
    source_id: str
    source_name: str
    citation_tag: str
    relevance_score: float
    evidence_type: str  # "semantic", "graph_neighborhood", etc.
    metadata: dict[str, Any] = field(default_factory=dict)


class EvidenceRanker:
    """Ranks and formats evidence for the LLM."""

    def __init__(self, max_evidence_items: int = 10) -> None:
        self._max_items = max_evidence_items

    def rank_and_format(self, context: RetrievedContext) -> list[RankedEvidence]:
        """Rank the retrieved context and assign citation tags."""
        evidence_items: list[RankedEvidence] = []
        citation_index = 1

        # 1. Process Semantic Chunks
        for result in context.semantic_chunks:
            chunk = result.chunk
            if not chunk.provenance:
                continue

            doc_name = chunk.provenance.document_name
            section = chunk.provenance.section or f"Page {chunk.provenance.page_number}"
            
            evidence_items.append(RankedEvidence(
                content=chunk.content,
                source_id=chunk.provenance.document_id,
                source_name=doc_name,
                citation_tag=f"[{citation_index}]",
                relevance_score=result.similarity_score,
                evidence_type="semantic",
                metadata={"section": section},
            ))
            citation_index += 1

        # 2. Process Graph Neighborhoods (treat as high-confidence structured facts)
        for neighborhood in context.graph_neighborhoods:
            asset_id = neighborhood["asset_id"]
            docs = len(neighborhood["neighborhood"]["documents"])
            wos = len(neighborhood["neighborhood"]["work_orders"])
            incidents = len(neighborhood["neighborhood"]["incidents"])
            
            # Create a synthetic text representation of the neighborhood
            content = (
                f"Asset {asset_id} is linked to {docs} documents, "
                f"{wos} work orders, and {incidents} incidents."
            )
            
            # Graph facts get a high baseline score (0.9)
            evidence_items.append(RankedEvidence(
                content=content,
                source_id="graph",
                source_name="Knowledge Graph",
                citation_tag=f"[{citation_index}]",
                relevance_score=0.90,
                evidence_type="graph_neighborhood",
                metadata={"asset_id": asset_id},
            ))
            citation_index += 1

        # 3. Sort by relevance
        evidence_items.sort(key=lambda x: x.relevance_score, reverse=True)

        # 4. Truncate to max items
        return evidence_items[:self._max_items]

    def build_prompt_context(self, evidence: list[RankedEvidence]) -> str:
        """Format the ranked evidence into a string for the LLM prompt."""
        if not evidence:
            return "No relevant evidence found in the knowledge base."

        lines = ["--- EVIDENCE CONTEXT ---"]
        for ev in evidence:
            lines.append(f"Citation: {ev.citation_tag}")
            lines.append(f"Source: {ev.source_name} (Type: {ev.evidence_type})")
            lines.append(f"Content: {ev.content}")
            lines.append("-" * 40)
        
        return "\n".join(lines)
