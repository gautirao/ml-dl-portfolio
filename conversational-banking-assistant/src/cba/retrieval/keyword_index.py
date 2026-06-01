import re
from typing import Protocol, runtime_checkable

from rank_bm25 import BM25Okapi  # type: ignore[import-untyped]

from cba.domain.models import Chunk, SearchResult
from cba.retrieval.metadata_filter import FilterCriteria, MetadataFilter


@runtime_checkable
class KeywordIndex(Protocol):
    def add_chunks(self, chunks: list[Chunk]) -> None:
        """
        Add or update chunks in the keyword index.
        """
        ...

    def search(
        self, query: str, criteria: FilterCriteria | None = None, top_k: int = 5
    ) -> list[SearchResult]:
        """
        Perform a keyword search using BM25.
        """
        ...


class BM25KeywordIndex:
    """
    Keyword index implementation using BM25Okapi.
    """

    def __init__(self) -> None:
        self.chunks: list[Chunk] = []
        self.bm25: BM25Okapi | None = None

    def _tokenize(self, text: str) -> list[str]:
        """
        Standard tokenizer: lowercase, strip punctuation, split by whitespace.
        """
        # Remove non-alphanumeric except spaces
        cleaned = re.sub(r"[^\w\s]", "", text.lower())
        return cleaned.split()

    def add_chunks(self, chunks: list[Chunk]) -> None:
        """
        Add chunks to the index. Note: In this simple implementation,
        adding chunks rebuilds the entire index.
        """
        self.chunks.extend(chunks)
        tokenized_corpus = [self._tokenize(chunk.text) for chunk in self.chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def search(
        self, query: str, criteria: FilterCriteria | None = None, top_k: int = 5
    ) -> list[SearchResult]:
        if not self.bm25 or not self.chunks:
            return []

        # 1. Filtering
        if criteria:
            filtered_chunks = MetadataFilter.filter_chunks(self.chunks, criteria)
            if not filtered_chunks:
                return []

            # If we filtered, we need to calculate scores only for filtered chunks.
            # BM25Okapi doesn't support easy sub-sampling, so we calculate for all
            # and then filter the results, OR rebuild a temporary index.
            # Rebuilding a temporary index for each filtered search is safer for score consistency.
            tokenized_corpus = [self._tokenize(chunk.text) for chunk in filtered_chunks]
            temp_bm25 = BM25Okapi(tokenized_corpus)

            tokenized_query = self._tokenize(query)
            scores = temp_bm25.get_scores(tokenized_query)

            results = []
            for chunk, score in zip(filtered_chunks, scores, strict=True):
                # In very small corpora, BM25 scores can be negative for matches.
                # We include any chunk that has at least one matching token.
                query_set = set(tokenized_query)
                chunk_set = set(self._tokenize(chunk.text))
                if query_set.intersection(chunk_set):
                    results.append(SearchResult(chunk=chunk, score=float(score)))

            # Sort by score descending
            results.sort(key=lambda x: x.score, reverse=True)
            return results[:top_k]

        # 2. No Filtering
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        results = []
        for chunk, score in zip(self.chunks, scores, strict=True):
            query_set = set(tokenized_query)
            chunk_set = set(self._tokenize(chunk.text))
            if query_set.intersection(chunk_set):
                results.append(SearchResult(chunk=chunk, score=float(score)))

        # Sort by score descending
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
