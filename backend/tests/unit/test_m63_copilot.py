"""Tests for M63 — Industrial Knowledge Copilot.

Validates:
1. Query Router (intent classification)
2. Mock LLM Generator (formatting and citations)
3. Full Copilot (end-to-end question answering)
"""
from __future__ import annotations

import pytest

from app.copilot.generator import MockLLMGenerator
from app.copilot.router import QueryIntent, QueryRouter
from app.domain.industrial.document import DocumentChunk, DocumentProvenance
from app.extraction.entities.extraction_pipeline import ExtractionPipeline
from app.knowledge.graph.industrial_graph_manager import IndustrialGraphManager
from app.knowledge.retrieval.embeddings import TFIDFEmbeddingModel
from app.knowledge.retrieval.hybrid_retriever import HybridRetriever
from app.knowledge.retrieval.vector_store import InMemoryVectorStore


class TestQueryRouter:
    def test_troubleshooting_intent(self):
        router = QueryRouter()
        assert router.route_query("Why did P-101 fail?") == QueryIntent.TROUBLESHOOTING
        assert router.route_query("What is the root cause of the pump issue?") == QueryIntent.TROUBLESHOOTING

    def test_status_intent(self):
        router = QueryRouter()
        assert router.route_query("What is the current status of P-101?") == QueryIntent.ASSET_STATUS
        assert router.route_query("Show me vibration condition for C-202") == QueryIntent.ASSET_STATUS

    def test_history_intent(self):
        router = QueryRouter()
        assert router.route_query("Show past work orders for V-100") == QueryIntent.MAINTENANCE_HISTORY
        assert router.route_query("Maintenance history of the compressor") == QueryIntent.MAINTENANCE_HISTORY

    def test_general_intent(self):
        router = QueryRouter()
        assert router.route_query("How does a centrifugal pump work?") == QueryIntent.GENERAL_KNOWLEDGE


class TestMockLLMGenerator:
    def test_generator_extracts_citations(self):
        generator = MockLLMGenerator()
        system_prompt = """
--- EVIDENCE CONTEXT ---
Citation: [1]
Source: doc1.txt (Type: semantic)
Content: P-101 has high vibration. This was found on Tuesday.
----------------------------------------
Citation: [2]
Source: Knowledge Graph (Type: graph_neighborhood)
Content: Asset P-101 is linked to 2 documents, 1 work orders, and 0 incidents.
----------------------------------------
--- END EVIDENCE CONTEXT ---
        """
        user_prompt = "What is wrong with P-101?"
        
        response = generator.generate(system_prompt, user_prompt)
        
        # The mock generator should extract the sentences and append the citation tag.
        assert "• P-101 has high vibration. [1]" in response
        assert "• Asset P-101 is linked to 2 documents, 1 work orders, and 0 incidents. [2]" in response

    def test_generator_deduplicates(self):
        generator = MockLLMGenerator()
        system_prompt = """
--- EVIDENCE CONTEXT ---
Citation: [1]
Source: doc1.txt
Content: The pump P-101 has high vibration issues! This needs fixing.
----------------------------------------
Citation: [2]
Source: doc2.txt
Content: The pump P-101 has high vibration issues! Also investigate the high temperature on the seal.
----------------------------------------
--- END EVIDENCE CONTEXT ---
        """
        user_prompt = "What is wrong with P-101?"
        
        response = generator.generate(system_prompt, user_prompt)
        
        # The duplicated sentence should only appear once (from citation [1])
        assert "• The pump P-101 has high vibration issues! [1]" in response
        assert "[2]" in response
        assert "• Also investigate the high temperature on the seal. [2]" in response
        # Should not duplicate the finding from [2]
        assert "• The pump P-101 has high vibration issues! [2]" not in response


class TestIndustrialCopilot:
    def test_end_to_end_copilot(self):
        from app.copilot.copilot import IndustrialCopilot
        
        # Setup infrastructure
        model = TFIDFEmbeddingModel(dim=128)
        store = InMemoryVectorStore()
        graph_manager = IndustrialGraphManager()
        extractor = ExtractionPipeline()
        
        # Setup mock data for P-101
        chunk = DocumentChunk(
            chunk_id="c1", document_id="d1", content="The drive-end bearing of P-101 seized completely due to lack of lubrication.",
            provenance=DocumentProvenance(document_id="d1", document_type="INCIDENT_REPORT", document_name="IN-44.txt", chunk_id="c1", extraction_method="text")
        )
        store.add_chunks([chunk], model.embed_batch([chunk.content]))
        
        from app.domain.industrial.asset import Asset
        graph_manager.builder.add_asset(Asset(id="P-101", name="P-101", equipment_tag="P-101", asset_type="Pump"))
        from app.domain.industrial.document import Document, DocumentType, DocumentFormat
        import datetime
        graph_manager.builder.add_document(Document(
            document_id="d1", name="IN-44.txt", document_type=DocumentType.INCIDENT_REPORT, document_format=DocumentFormat.TXT, file_hash="123", file_path="IN-44.txt", file_size_bytes=100, ingested_at=datetime.datetime.now()
        ))
        graph_manager.builder.link_document_to_asset("d1", "P-101")
        
        retriever = HybridRetriever(model, store, graph_manager, extractor)
        copilot = IndustrialCopilot(retriever)
        
        # Ask a troubleshooting question
        response = copilot.ask("Why did P-101 fail?")
        
        # Verify routing
        assert response.intent == "troubleshooting"
        
        # Verify evidence was retrieved
        assert len(response.evidence) == 2  # 1 semantic + 1 graph neighborhood
        
        # Verify answer is grounded
        assert "seized completely due to lack of lubrication" in response.answer
        assert "[1]" in response.answer or "[2]" in response.answer

    def test_no_evidence(self):
        from app.copilot.copilot import IndustrialCopilot
        
        model = TFIDFEmbeddingModel(dim=128)
        store = InMemoryVectorStore()  # empty
        graph_manager = IndustrialGraphManager()  # empty
        
        retriever = HybridRetriever(model, store, graph_manager)
        copilot = IndustrialCopilot(retriever)
        
        response = copilot.ask("Why did P-999 fail?")
        
        assert len(response.evidence) == 0
        assert "cannot find evidence" in response.answer
