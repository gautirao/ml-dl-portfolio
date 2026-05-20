import os
from datetime import datetime
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup
from pypdf import PdfReader

from .models import Source, SourceType, ExtractedDocument, ExtractedPage

class DocumentExtractor:
    def __init__(self, project_root: Path = Path(".")):
        self.project_root = project_root

    def extract(self, source: Source) -> ExtractedDocument:
        """
        Dispatches extraction based on source_type.
        """
        full_path = self.project_root / source.local_path
        if not full_path.exists():
            raise FileNotFoundError(f"Source file not found at: {source.local_path} (full path: {full_path})")

        if source.source_type == SourceType.PUBLIC_PDF:
            return self._extract_pdf(source, full_path)
        elif source.source_type == SourceType.PUBLIC_WEB:
            return self._extract_html(source, full_path)
        else:
            raise ValueError(f"Unsupported source type for extraction: {source.source_type}")

    def _extract_pdf(self, source: Source, full_path: Path) -> ExtractedDocument:
        pages: List[ExtractedPage] = []
        reader = PdfReader(full_path)
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages.append(ExtractedPage(page_number=i + 1, text=text.strip()))
            
        return ExtractedDocument(
            source_id=source.source_id,
            title=source.title,
            document_type=source.document_type,
            product_area=source.product_area,
            local_path=source.local_path,
            extracted_at=datetime.now(),
            pages=pages
        )

    def _extract_html(self, source: Source, full_path: Path) -> ExtractedDocument:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        soup = BeautifulSoup(content, "html.parser")
        
        # Remove script, style, and noscript elements
        for element in soup(["script", "style", "noscript"]):
            element.decompose()
            
        # Extract visible text
        text = soup.get_text(separator="\n", strip=True)
        
        # HTML is treated as a single page (page 1)
        pages = [ExtractedPage(page_number=1, text=text)]
        
        return ExtractedDocument(
            source_id=source.source_id,
            title=source.title,
            document_type=source.document_type,
            product_area=source.product_area,
            local_path=source.local_path,
            extracted_at=datetime.now(),
            pages=pages
        )
