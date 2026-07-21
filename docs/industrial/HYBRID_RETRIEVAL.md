# Hybrid Retrieval

Standard RAG (Retrieval-Augmented Generation) systems rely entirely on vector embeddings to find relevant context. In heavy industry, semantic similarity often fails (e.g., "Pump P-101 failure" and "Pump P-102 failure" are semantically identical, but operationally entirely different).

PIA Industrial utilizes a **Hybrid Retrieval** architecture (`app.knowledge.retrieval`).

## Retrieval Methodology

1. **Exact Identifier Retrieval**: If an NLP extractor identifies a canonical asset ID (e.g., `P-101`), the system immediately fetches the explicit topological neighborhood of that node from the Knowledge Graph (its components, active work orders, recent inspections).
2. **Vector Similarity**: For ambiguous or descriptive queries (e.g., "What causes high vibration?"), the system falls back to semantic vector embeddings (via SentenceTransformers or TF-IDF in offline mode) to find historical similar events.
3. **Hybrid Ranking**: The results from the Graph traversal and the Vector search are merged. Facts explicitly linked in the graph are weighted higher than semantically similar documents from unrelated assets.

## Citation Preservation

Every retrieved fact retains its original source metadata. When the LLM Copilot generates an answer, it must include these inline citations. The Hybrid Retriever strictly blocks orphaned LLM assertions that cannot be traced back to the retrieved graph topology.
