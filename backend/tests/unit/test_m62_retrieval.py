"""Tests for M62 — Semantic Retrieval & Hybrid RAG.

Validates:
1. TF-IDF Embeddings
2. In-Memory Vector Store
3. Hybrid Retriever
4. Evidence Ranker
"""
from __future__ import annotations

import pytest

from app.domain.industrial.document import DocumentChunk, DocumentProvenance
from app.extraction.entities.extraction_pipeline import ExtractionPipeline
from app.knowledge.graph.industrial_graph_manager import IndustrialGraphManager
from app.knowledge.retrieval.embeddings import TFIDFEmbeddingModel
from app.knowledge.retrieval.evidence_ranker import EvidenceRanker
from app.knowledge.retrieval.hybrid_retriever import HybridRetriever
from app.knowledge.retrieval.vector_store import InMemoryVectorStore


class TestEmbeddings:
    def test_tfidf_embedding(self):
        model = TFIDFEmbeddingModel(dim=128)
        assert model.dimension == 128
        
        v1 = model.embed_text("centrifugal pump bearing failure")
        v2 = model.embed_text("pump bearing seized")
        v3 = model.embed_text("the quick brown fox")

        assert len(v1) == 128
        assert len(v2) == 128

        # v1 and v2 should be more similar to each other than to v3
        def dot(a, b): return sum(x * y for x, y in zip(a, b))
        
        sim12 = dot(v1, v2)
        sim13 = dot(v1, v3)
        assert sim12 > sim13


class TestVectorStore:
    def test_in_memory_store(self):
        model = TFIDFEmbeddingModel(dim=128)
        store = InMemoryVectorStore()

        chunks = [
            DocumentChunk(
                chunk_id="c1", document_id="d1", content="pump vibration is high",
                provenance=DocumentProvenance(document_id="d1", document_type="INSPECTION_REPORT", document_name="doc1", chunk_id="c1", extraction_method="text")
            ),
            DocumentChunk(
                chunk_id="c2", document_id="d2", content="replace the seal",
                provenance=DocumentProvenance(document_id="d2", document_type="WORK_ORDER", document_name="doc2", chunk_id="c2", extraction_method="text")
            ),
        ]
        
        embeddings = model.embed_batch([c.content for c in chunks])
        store.add_chunks(chunks, embeddings)

        query_emb = model.embed_text("vibration")
        results = store.search(query_emb, top_k=1)
        
        assert len(results) == 1
        assert results[0].chunk.chunk_id == "c1"

    def test_vector_store_filters(self):
        model = TFIDFEmbeddingModel(dim=128)
        store = InMemoryVectorStore()

        chunks = [
            DocumentChunk(
                chunk_id="c1", document_id="d1", content="pump",
                provenance=DocumentProvenance(document_id="d1", document_type="INSPECTION_REPORT", document_name="doc1", chunk_id="c1", extraction_method="text")
            ),
            DocumentChunk(
                chunk_id="c2", document_id="d2", content="pump",
                provenance=DocumentProvenance(document_id="d2", document_type="WORK_ORDER", document_name="doc2", chunk_id="c2", extraction_method="text")
            ),
        ]
        embeddings = model.embed_batch([c.content for c in chunks])
        store.add_chunks(chunks, embeddings)

        query_emb = model.embed_text("pump")
        
        # Search with filter
        results = store.search(query_emb, filters={"document_type": "WORK_ORDER"})
        assert len(results) == 1
        assert results[0].chunk.chunk_id == "c2"


class TestHybridRetriever:
    def test_hybrid_retrieval(self):
        model = TFIDFEmbeddingModel(dim=128)
        store = InMemoryVectorStore()
        graph_manager = IndustrialGraphManager()
        extractor = ExtractionPipeline()

        # Add a chunk to vector store
        chunk = DocumentChunk(
            chunk_id="c1", document_id="d1", content="P-101 vibration is high",
            provenance=DocumentProvenance(document_id="d1", document_type="INSPECTION_REPORT", document_name="doc1", chunk_id="c1", extraction_method="text")
        )
        store.add_chunks([chunk], model.embed_batch([chunk.content]))

        # Add graph data for P-101
        from app.domain.industrial.asset import Asset
        graph_manager.builder.add_asset(Asset(id="P-101", name="P-101", equipment_tag="P-101", asset_type="Pump"))
        from app.domain.industrial.document import Document, DocumentType, DocumentFormat
        import datetime
        graph_manager.builder.add_document(Document(
            document_id="d1", name="doc1", document_type=DocumentType.INSPECTION_REPORT, document_format=DocumentFormat.PDF, file_hash="123", file_path="doc1", file_size_bytes=100, ingested_at=datetime.datetime.now()
        ))
        graph_manager.builder.link_document_to_asset("d1", "P-101")

        retriever = HybridRetriever(model, store, graph_manager, extractor)
        
        # The query asks about P-101, so it should hit semantic search AND graph neighborhood
        context = retriever.retrieve("What is wrong with P-101?")
        
        assert len(context.semantic_chunks) == 1
        assert context.semantic_chunks[0].chunk.chunk_id == "c1"
        
        assert len(context.graph_entities) >= 1
        assert any(e["value"] == "P-101" for e in context.graph_entities)
        
        assert len(context.graph_neighborhoods) >= 1
        assert context.graph_neighborhoods[0]["asset_id"] == "P-101"


class TestEvidenceRanker:
    def test_rank_and_format(self):
        model = TFIDFEmbeddingModel(dim=128)
        store = InMemoryVectorStore()
        graph_manager = IndustrialGraphManager()
        extractor = ExtractionPipeline()
        
        # Add mock semantic chunk
        chunk = DocumentChunk(
            chunk_id="c1", document_id="d1", content="P-101 vibration is high",
            provenance=DocumentProvenance(document_id="d1", document_type="INSPECTION_REPORT", document_name="doc1.txt", chunk_id="c1", extraction_method="text")
        )
        store.add_chunks([chunk], model.embed_batch([chunk.content]))
        
        # Add mock graph
        from app.domain.industrial.asset import Asset
        from app.domain.industrial.document import Document
        graph_manager.builder.add_asset(Asset(id="P-101", name="P-101", equipment_tag="P-101", asset_type="Pump"))
        graph_manager.builder.add_document(Document(document_id="d1", name="doc1", document_type="INSPECTION", document_format="txt", file_hash="hash"))
        graph_manager.builder.link_document_to_asset("d1", "P-101")

        retriever = HybridRetriever(model, store, graph_manager, extractor)
        context = retriever.retrieve("P-101 status")
        
        ranker = EvidenceRanker()
        evidence = ranker.rank_and_format(context)
        
        assert len(evidence) == 2
        
        # One from graph, one from semantic
        types = {e.evidence_type for e in evidence}
        assert "graph_neighborhood" in types
        assert "semantic" in types
        
        # Graph should be ranked high (0.90)
        assert any(e.relevance_score == 0.90 for e in evidence)

        # Build prompt
        prompt = ranker.build_prompt_context(evidence)
        assert "doc1.txt" in prompt
        assert "Knowledge Graph" in prompt
