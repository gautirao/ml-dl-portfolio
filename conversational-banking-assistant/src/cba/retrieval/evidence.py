from datetime import UTC, datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, Field

from cba.domain.models import Chunk, SearchResult
from cba.retrieval.metadata_filter import FilterCriteria


class RetrievalMethod(StrEnum):
    VECTOR = "vector"
    KEYWORD = "keyword"
    METADATA = "metadata"


class EvidenceItem(BaseModel):
    chunk: Chunk
    retrieval_methods: list[RetrievalMethod]
    scores_by_method: dict[RetrievalMethod, float]
    ranks_by_method: dict[RetrievalMethod, int]
    matched_terms: list[str] | None = None

    @property
    def chunk_id(self) -> str:
        return self.chunk.chunk_id

    @property
    def text(self) -> str:
        return self.chunk.text

    @property
    def source_id(self) -> str:
        return self.chunk.source_id

    @property
    def citation_label(self) -> str:
        return self.chunk.citation_label

    @property
    def section_heading(self) -> str | None:
        return self.chunk.section_heading

    @property
    def page_number_start(self) -> int | None:
        return self.chunk.page_number_start

    @property
    def page_number_end(self) -> int | None:
        return self.chunk.page_number_end

    @property
    def chunk_hash(self) -> str:
        return self.chunk.chunk_hash

    def get_best_rank(self) -> int:
        if not self.ranks_by_method:
            return 999  # Large fallback
        return min(self.ranks_by_method.values())


class EvidencePacket(BaseModel):
    question: str
    items: list[EvidenceItem] = Field(default_factory=list)
    filters_applied: FilterCriteria | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    limitations: list[str] = Field(default_factory=list)

    @property
    def total_items(self) -> int:
        return len(self.items)

    @property
    def unique_source_ids(self) -> set[str]:
        return {item.source_id for item in self.items}

    @property
    def is_empty(self) -> bool:
        return self.total_items == 0

    @property
    def retrieval_methods_used(self) -> list[RetrievalMethod]:
        methods = set()
        for item in self.items:
            methods.update(item.retrieval_methods)
        return sorted(list(methods))

    @classmethod
    def from_results(
        cls,
        question: str,
        vector_results: list[SearchResult] | None = None,
        keyword_results: list[SearchResult] | None = None,
        filters_applied: FilterCriteria | None = None,
    ) -> Self:
        """
        Factory method to create a packet from raw search results, 
        performing deduplication and deterministic sorting.
        """
        evidence_map: dict[str, EvidenceItem] = {}
        
        # Process Vector Results
        if vector_results:
            for i, res in enumerate(vector_results):
                cls._add_to_map(
                    evidence_map, 
                    res, 
                    RetrievalMethod.VECTOR, 
                    rank=i + 1
                )
                
        # Process Keyword Results
        if keyword_results:
            for i, res in enumerate(keyword_results):
                cls._add_to_map(
                    evidence_map, 
                    res, 
                    RetrievalMethod.KEYWORD, 
                    rank=i + 1
                )
        
        # Sort items: 
        # 1. best rank across methods
        # 2. original insertion (implicit in dict order in Python 3.7+, but let's be safe)
        # 3. chunk_id
        items = list(evidence_map.values())
        items.sort(key=lambda x: (x.get_best_rank(), x.chunk_id))
        
        return cls(
            question=question,
            items=items,
            filters_applied=filters_applied
        )

    @staticmethod
    def _add_to_map(
        evidence_map: dict[str, EvidenceItem], 
        res: SearchResult, 
        method: RetrievalMethod,
        rank: int
    ) -> None:
        chunk_id = res.chunk.chunk_id
        if chunk_id in evidence_map:
            item = evidence_map[chunk_id]
            if method not in item.retrieval_methods:
                item.retrieval_methods.append(method)
            item.scores_by_method[method] = res.score
            item.ranks_by_method[method] = rank
        else:
            evidence_map[chunk_id] = EvidenceItem(
                chunk=res.chunk,
                retrieval_methods=[method],
                scores_by_method={method: res.score},
                ranks_by_method={method: rank}
            )

    def to_context_blocks(self) -> str:
        """
        Formats evidence items into context blocks for downstream use.
        """
        if self.is_empty:
            return ""

        blocks = []
        for item in self.items:
            citation = f"[{item.citation_label}]"
            section = f" Section: {item.section_heading}" if item.section_heading else ""
            
            page_info = ""
            if item.page_number_start:
                if item.page_number_end and item.page_number_end != item.page_number_start:
                    page_info = f" (Pages {item.page_number_start}-{item.page_number_end})"
                else:
                    page_info = f" (Page {item.page_number_start})"

            header = f"{citation}{section}{page_info}"
            separator = "-" * len(header)
            
            block = (
                f"{header}\n"
                f"{separator}\n"
                f"{item.text}\n"
                f"{separator}\n"
                f"Source: {item.source_id} | Chunk: {item.chunk_id}"
            )
            blocks.append(block)

        return "\n\n".join(blocks)
