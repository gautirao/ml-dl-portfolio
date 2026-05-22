from pydantic import BaseModel

from cba.domain.enums import DocumentType, ProductArea
from cba.domain.models import Chunk


class FilterCriteria(BaseModel):
    source_id: str | None = None
    document_type: DocumentType | None = None
    product_area: ProductArea | None = None
    section_heading: str | None = None
    citation_label: str | None = None
    page_number_start: int | None = None
    page_number_end: int | None = None
    chunk_index: int | None = None
    chunk_hash: str | None = None

class MetadataFilter:
    """
    Utility for filtering chunks based on metadata criteria.
    """
    @staticmethod
    def filter_chunks(chunks: list[Chunk], criteria: FilterCriteria) -> list[Chunk]:
        """
        Filter a list of chunks based on provided criteria (AND logic).
        """
        filtered = chunks
        
        if criteria.source_id is not None:
            filtered = [c for c in filtered if c.source_id == criteria.source_id]
            
        if criteria.document_type is not None:
            filtered = [c for c in filtered if c.document_type == criteria.document_type]
            
        if criteria.product_area is not None:
            filtered = [c for c in filtered if c.product_area == criteria.product_area]
            
        if criteria.section_heading is not None:
            filtered = [c for c in filtered if c.section_heading == criteria.section_heading]
            
        if criteria.citation_label is not None:
            filtered = [c for c in filtered if c.citation_label == criteria.citation_label]
            
        if criteria.page_number_start is not None:
            filtered = [c for c in filtered if c.page_number_start == criteria.page_number_start]
            
        if criteria.page_number_end is not None:
            filtered = [c for c in filtered if c.page_number_end == criteria.page_number_end]
            
        if criteria.chunk_index is not None:
            filtered = [c for c in filtered if c.chunk_index == criteria.chunk_index]
            
        if criteria.chunk_hash is not None:
            filtered = [c for c in filtered if c.chunk_hash == criteria.chunk_hash]
            
        return filtered
