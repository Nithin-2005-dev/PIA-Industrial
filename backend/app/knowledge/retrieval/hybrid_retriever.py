"""Hybrid Retriever for Industrial Intelligence.

Combines semantic vector search with structured graph traversal
to provide highly grounded context for generation.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from app.domain.industrial.document import DocumentChunk
from app.extraction.entities.extraction_pipeline import ExtractionPipeline
from app.knowledge.graph.industrial_graph_manager import IndustrialGraphManager
from app.knowledge.retrieval.embeddings import EmbeddingModel
from app.knowledge.retrieval.vector_store import SearchResult, VectorStore

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RetrievedContext:
    """The result of a hybrid retrieval query."""
    query: str
    semantic_chunks: tuple[SearchResult, ...]
    graph_entities: tuple[dict[str, Any], ...]
    graph_neighborhoods: tuple[dict[str, Any], ...]
    metadata: dict[str, Any] = field(default_factory=dict)


class HybridRetriever:
    """Combines semantic search with graph traversal."""

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        vector_store: VectorStore,
        graph_manager: IndustrialGraphManager,
        extraction_pipeline: ExtractionPipeline | None = None,
    ) -> None:
        self._embedding_model = embedding_model
        self._vector_store = vector_store
        self._graph_manager = graph_manager
        # Use extraction pipeline to find entities in the query
        self._extractor = extraction_pipeline or ExtractionPipeline()

    def retrieve(
        self,
        query: str,
        top_k_semantic: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> RetrievedContext:
        """Perform a hybrid search for the query."""
        logger.info(f"Hybrid retrieval for query: '{query}'")

        # 1. Semantic Search
        query_embedding = self._embedding_model.embed_text(query)
        semantic_results = self._vector_store.search(
            query_embedding,
            top_k=top_k_semantic,
            filters=filters,
        )

        # 2. Graph Entity Extraction from Query
        # What industrial entities is the user asking about?
        query_entities = self._extractor.extract_from_text(query)
        
        graph_entities: list[dict[str, Any]] = []
        for e in query_entities:
            graph_entities.append({
                "type": e.entity_type,
                "value": e.canonical_value,
            })

        # 3. Graph Traversal (Neighborhoods)
        # If the user asks about an asset, fetch its neighborhood
        neighborhoods: list[dict[str, Any]] = []
        for e in query_entities:
            if e.entity_type == "equipment_tag":
                neighborhood = self._graph_manager.get_asset_neighborhood(e.canonical_value)
                # Only include if there is actually some linked data
                total_links = sum(len(items) for items in neighborhood.values())
                if total_links > 0:
                    neighborhoods.append({
                        "asset_id": e.canonical_value,
                        "neighborhood": neighborhood,
                    })

        # Return combined context
        return RetrievedContext(
            query=query,
            semantic_chunks=tuple(semantic_results),
            graph_entities=tuple(graph_entities),
            graph_neighborhoods=tuple(neighborhoods),
            metadata={
                "extracted_entities": len(query_entities),
                "semantic_matches": len(semantic_results),
                "neighborhoods_found": len(neighborhoods),
            },
        )
