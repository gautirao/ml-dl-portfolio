
import pytest

from cba.domain.models import Chunk, DocumentType, ProductArea
from cba.retrieval.embeddings import FakeEmbeddingModel
from cba.retrieval.vector_index import QdrantVectorIndex


@pytest.fixture
def fake_embedding_model():
    return FakeEmbeddingModel(dimension=384)

@pytest.fixture
def sample_chunk():
    return Chunk(
        chunk_id="test-source::chunk::0001",
        source_id="test-source",
        citation_label="Test Label",
        title="Test Title",
        document_type=DocumentType.TERMS_CONDITIONS,
        product_area=ProductArea.CURRENT_ACCOUNTS,
        section_heading="Test Section",
        chunk_index=1,
        text="This is a test chunk of text about banking policies.",
        character_start=0,
        character_end=52,
        page_number_start=1,
        chunk_hash="fakehash123"
    )

def test_vector_store_path_safety(fake_embedding_model):
    # Should fail if path is not under data/vector_store/
    msg = "Persistent vector store must be under data/vector_store/"
    with pytest.raises(ValueError, match=msg):
        QdrantVectorIndex(embedding_model=fake_embedding_model, path="/tmp/unsafe_qdrant")

def test_add_and_search_chunks(fake_embedding_model, sample_chunk):
    index = QdrantVectorIndex(embedding_model=fake_embedding_model, location=":memory:")
    
    index.add_chunks([sample_chunk])
    
    # Search for something similar (FakeEmbeddingModel uses hash, so exact text is best)
    results = index.search("This is a test chunk of text about banking policies.", top_k=1)
    
    assert len(results) == 1
    assert results[0].chunk.chunk_id == sample_chunk.chunk_id
    assert results[0].chunk.text == sample_chunk.text
    assert results[0].score > 0.9 # Should be high similarity for exact match

def test_metadata_preservation(fake_embedding_model, sample_chunk):
    index = QdrantVectorIndex(embedding_model=fake_embedding_model, location=":memory:")
    index.add_chunks([sample_chunk])
    
    results = index.search("banking policies", top_k=1)
    retrieved = results[0].chunk
    
    assert retrieved.citation_label == sample_chunk.citation_label
    assert retrieved.title == sample_chunk.title
    assert retrieved.document_type == sample_chunk.document_type
    assert retrieved.product_area == sample_chunk.product_area
    assert retrieved.section_heading == sample_chunk.section_heading
    assert retrieved.chunk_hash == sample_chunk.chunk_hash
    assert retrieved.page_number_start == sample_chunk.page_number_start

def test_duplicate_chunk_id_handling(fake_embedding_model, sample_chunk):
    index = QdrantVectorIndex(embedding_model=fake_embedding_model, location=":memory:")
    
    # Add same chunk twice
    index.add_chunks([sample_chunk])
    index.add_chunks([sample_chunk])
    
    # Check collection count (using internal client)
    count = index.client.count(collection_name=index.COLLECTION_NAME).count
    assert count == 1

def test_update_chunk_payload(fake_embedding_model, sample_chunk):
    index = QdrantVectorIndex(embedding_model=fake_embedding_model, location=":memory:")
    index.add_chunks([sample_chunk])
    
    # Update the chunk with different text
    updated_chunk = sample_chunk.model_copy(update={"text": "Updated text content"})
    index.add_chunks([updated_chunk])
    
    results = index.search("Updated text content", top_k=1)
    assert results[0].chunk.text == "Updated text content"
    
    count = index.client.count(collection_name=index.COLLECTION_NAME).count
    assert count == 1

def test_empty_index_search(fake_embedding_model):
    index = QdrantVectorIndex(embedding_model=fake_embedding_model, location=":memory:")
    results = index.search("query", top_k=5)
    assert results == []

def test_search_score_semantics(fake_embedding_model, sample_chunk):
    index = QdrantVectorIndex(embedding_model=fake_embedding_model, location=":memory:")
    index.add_chunks([sample_chunk])
    
    # In Qdrant COSINE distance, higher score is better (1.0 is exact match)
    results = index.search(sample_chunk.text, top_k=1)
    assert results[0].score > 0.99
