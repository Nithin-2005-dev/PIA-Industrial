"""Entity Extraction Pipeline.

Orchestrates the 4-layer extraction architecture:
1. Regex extraction (deterministic, highest confidence)
2. Dictionary matching (known terms)
3. (Future: LLM-assisted extraction)
4. Validation & resolution

Input: Document chunks (from ingestion pipeline)
Output: Resolved entities ready for knowledge graph
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from app.domain.industrial.document import DocumentChunk
from app.extraction.entities.dictionary_extractor import DictionaryExtractor
from app.extraction.entities.entity_resolver import EntityResolver, ResolvedEntity
from app.extraction.entities.regex_extractor import ExtractedEntity, RegexExtractor

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ChunkExtractionResult:
    """Extraction result for a single chunk."""
    chunk_id: str
    document_id: str
    raw_entities: tuple[ExtractedEntity, ...]
    resolved_entities: tuple[ResolvedEntity, ...]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DocumentExtractionResult:
    """Extraction result for a complete document."""
    document_id: str
    chunk_results: tuple[ChunkExtractionResult, ...]
    all_resolved_entities: tuple[ResolvedEntity, ...]
    entity_summary: dict[str, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class ExtractionPipeline:
    """Orchestrates entity extraction from document chunks.

    Usage:
        pipeline = ExtractionPipeline()
        result = pipeline.extract_from_chunks(chunks, document_id)
    """

    def __init__(
        self,
        min_confidence: float = 0.3,
    ) -> None:
        self._regex_extractor = RegexExtractor()
        self._dictionary_extractor = DictionaryExtractor()
        self._resolver = EntityResolver(min_confidence=min_confidence)

    def extract_from_chunks(
        self,
        chunks: list[DocumentChunk],
        document_id: str,
    ) -> DocumentExtractionResult:
        """Extract entities from all chunks of a document.

        Steps per chunk:
        1. Run regex extractor
        2. Run dictionary extractor
        3. Merge all raw entities
        4. Resolve and deduplicate

        Then aggregate across all chunks:
        5. Document-level deduplication and resolution
        6. Build entity summary
        """
        chunk_results: list[ChunkExtractionResult] = []
        all_raw_entities: list[ExtractedEntity] = []

        for chunk in chunks:
            # Layer 1: Regex extraction
            regex_entities = self._regex_extractor.extract(chunk.content)

            # Layer 2: Dictionary matching
            dict_entities = self._dictionary_extractor.extract(chunk.content)

            # Merge raw entities
            chunk_raw = regex_entities + dict_entities
            all_raw_entities.extend(chunk_raw)

            # Per-chunk resolution
            chunk_resolved = self._resolver.resolve(chunk_raw)

            chunk_results.append(ChunkExtractionResult(
                chunk_id=chunk.chunk_id,
                document_id=document_id,
                raw_entities=tuple(chunk_raw),
                resolved_entities=tuple(chunk_resolved),
            ))

        # Document-level resolution (dedup across chunks)
        document_resolved = self._resolver.resolve(all_raw_entities)

        # Build summary
        entity_summary: dict[str, int] = {}
        for entity in document_resolved:
            entity_summary[entity.entity_type] = (
                entity_summary.get(entity.entity_type, 0) + 1
            )

        logger.info(
            f"Extracted {len(document_resolved)} entities from "
            f"{len(chunks)} chunks of {document_id}: {entity_summary}"
        )

        return DocumentExtractionResult(
            document_id=document_id,
            chunk_results=tuple(chunk_results),
            all_resolved_entities=tuple(document_resolved),
            entity_summary=entity_summary,
        )

    def extract_from_text(self, text: str) -> list[ResolvedEntity]:
        """Convenience method: extract entities from raw text."""
        regex_entities = self._regex_extractor.extract(text)
        dict_entities = self._dictionary_extractor.extract(text)
        return self._resolver.resolve(regex_entities + dict_entities)
