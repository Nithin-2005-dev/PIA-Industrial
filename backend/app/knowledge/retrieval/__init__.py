"""Semantic Retrieval and Hybrid RAG.

This package provides intelligence retrieval for PIA Industrial.
It combines vector-based semantic search with graph-based structured
search to form a Hybrid RAG (Retrieval-Augmented Generation) system.

Key components:
1. Embeddings: text -> vector conversion
2. Vector Store: similarity search for document chunks
3. Hybrid Retriever: combines vector search and graph traversal
4. Evidence Ranker: ranks and grounds retrieved context with citations
"""
