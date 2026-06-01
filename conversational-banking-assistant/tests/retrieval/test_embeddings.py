import pytest

from cba.retrieval.embeddings import FakeEmbeddingModel


def test_fake_embedding_model_dimension() -> None:
    dim = 128
    model = FakeEmbeddingModel(dimension=dim)
    vec = model.embed_query("test")
    assert len(vec) == dim


def test_fake_embedding_model_determinism() -> None:
    model = FakeEmbeddingModel()
    text = "banking policies"
    vec1 = model.embed_query(text)
    vec2 = model.embed_query(text)
    assert vec1 == vec2


def test_fake_embedding_model_different_texts() -> None:
    model = FakeEmbeddingModel()
    vec1 = model.embed_query("text one")
    vec2 = model.embed_query("text two")
    assert vec1 != vec2


def test_fake_embedding_model_normalization() -> None:
    model = FakeEmbeddingModel()
    vec = model.embed_query("test normalization")
    norm = sum(x * x for x in vec) ** 0.5
    assert pytest.approx(norm, rel=1e-5) == 1.0
