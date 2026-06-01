from pydantic import BaseModel

from cba.retrieval.evidence import EvidenceItem, EvidencePacket, RetrievalMethod
from cba.retrieval.keyword_index import KeywordIndex
from cba.retrieval.metadata_filter import FilterCriteria, MetadataFilter
from cba.retrieval.vector_index import VectorIndex


class HybridRetrievalConfig(BaseModel):
    rrf_k: int = 60
    vector_top_k: int = 10
    keyword_top_k: int = 10


class HybridRetriever:
    """
    Hybrid retriever that combines vector and keyword search results using
    Reciprocal Rank Fusion (RRF).
    """

    def __init__(
        self,
        vector_index: VectorIndex,
        keyword_index: KeywordIndex,
        config: HybridRetrievalConfig | None = None,
    ):
        self.vector_index = vector_index
        self.keyword_index = keyword_index
        self.config = config or HybridRetrievalConfig()

    def retrieve(
        self, query: str, criteria: FilterCriteria | None = None, top_k: int = 5
    ) -> EvidencePacket:
        # 1. Fetch results from both indexes
        vector_results = self.vector_index.search(query, top_k=self.config.vector_top_k)
        keyword_results = self.keyword_index.search(query, top_k=self.config.keyword_top_k)

        # 2. Apply metadata filters (Post-filtering)
        if criteria:
            vector_results = [
                res for res in vector_results if MetadataFilter.filter_chunks([res.chunk], criteria)
            ]
            keyword_results = [
                res
                for res in keyword_results
                if MetadataFilter.filter_chunks([res.chunk], criteria)
            ]

        # 3. RRF Fusion
        # We need to map chunk_id -> EvidenceItem
        evidence_map: dict[str, EvidenceItem] = {}
        rrf_scores: dict[str, float] = {}

        # Process Vector Results
        for i, res in enumerate(vector_results):
            rank = i + 1
            chunk_id = res.chunk.chunk_id

            # Update RRF score
            rrf_score = 1.0 / (self.config.rrf_k + rank)
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + rrf_score

            # Create or update EvidenceItem
            evidence_map[chunk_id] = EvidenceItem(
                chunk=res.chunk,
                retrieval_methods=[RetrievalMethod.VECTOR],
                scores_by_method={RetrievalMethod.VECTOR: res.score},
                ranks_by_method={RetrievalMethod.VECTOR: rank},
            )

        # Process Keyword Results
        for i, res in enumerate(keyword_results):
            rank = i + 1
            chunk_id = res.chunk.chunk_id

            # Update RRF score
            rrf_score = 1.0 / (self.config.rrf_k + rank)
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + rrf_score

            if chunk_id in evidence_map:
                item = evidence_map[chunk_id]
                item.retrieval_methods.append(RetrievalMethod.KEYWORD)
                item.scores_by_method[RetrievalMethod.KEYWORD] = res.score
                item.ranks_by_method[RetrievalMethod.KEYWORD] = rank
            else:
                evidence_map[chunk_id] = EvidenceItem(
                    chunk=res.chunk,
                    retrieval_methods=[RetrievalMethod.KEYWORD],
                    scores_by_method={RetrievalMethod.KEYWORD: res.score},
                    ranks_by_method={RetrievalMethod.KEYWORD: rank},
                )

        # 4. Deterministic Sorting
        # Rules:
        # 1. RRF score descending
        # 2. best rank ascending
        # 3. chunk_id ascending
        sorted_chunk_ids = sorted(
            evidence_map.keys(),
            key=lambda cid: (
                -rrf_scores[cid],  # RRF Score (desc)
                evidence_map[cid].get_best_rank(),  # Best Rank (asc)
                cid,  # chunk_id (asc)
            ),
        )

        final_items = [evidence_map[cid] for cid in sorted_chunk_ids[:top_k]]

        return EvidencePacket(question=query, items=final_items, filters_applied=criteria)
