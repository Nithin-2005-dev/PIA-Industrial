import pytest
from app.ingestion.chunking.chunker import ChunkingEngine, ChunkingConfig

def test_semantic_split_respects_boundaries():
    config = ChunkingConfig(max_chunk_size=100, chunk_overlap=20)
    engine = ChunkingEngine(config)
    
    text = "This is a sentence. This is another sentence that is quite long and we want to see how the chunker handles it. This is a third sentence."
    
    # max_chunk_size = 100.
    # Sentences: 19, 92, 28 chars.
    chunks = engine._split_text(text)
    
    # Ensure no word is cut in half
    assert len(chunks) == 3
    assert "This is a sentence." == chunks[0].strip()
    assert "This is another sentence that is quite long and we want to see how the chunker handles it." == chunks[1].strip()
    assert "This is a third sentence." == chunks[2].strip()
    
def test_semantic_split_long_sentence():
    config = ChunkingConfig(max_chunk_size=30, chunk_overlap=10)
    engine = ChunkingEngine(config)
    
    text = "This is an extraordinarily long sentence that cannot possibly fit into a single thirty character chunk no matter what."
    chunks = engine._split_text(text)
    
    # Should split on word boundaries
    assert "This is an extraordinarily" in chunks[0]
    assert "long sentence that cannot" in chunks[1]

def test_no_fragments_like_ignificant():
    config = ChunkingConfig(max_chunk_size=50, chunk_overlap=10)
    engine = ChunkingEngine(config)
    text = "We found a significant maintenance activity on the primary pump P-204 so that we can ensure operations continue."
    chunks = engine._split_text(text)
    
    # Ensure no words are sliced
    for chunk in chunks:
        words = chunk.split()
        for w in words:
            assert w not in ["ignificant", "perations", "ward"]
