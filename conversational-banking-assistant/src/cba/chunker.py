import hashlib
import re
from typing import List, Optional
from .models import ExtractedDocument, Chunk

class TextCleaner:
    def __init__(self):
        # Heuristics for boilerplate removal
        self.boilerplate_patterns = [
            r"^Skip to main content$",
            r"^Log in$",
            r"^Menu$",
            r"^Close$",
            r"^NatWest Personal Banking$",
            r"^Footer:.*$",
            r"^Page \d+ Footer$"
        ]

    def clean(self, text: str) -> str:
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            # Check against boilerplate patterns
            if any(re.match(pattern, stripped, re.IGNORECASE) for pattern in self.boilerplate_patterns):
                continue
            cleaned_lines.append(line) # Keep original line to preserve structure initially

        cleaned_text = "\n".join(cleaned_lines)
        
        # Normalize whitespace
        cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)
        cleaned_text = re.sub(r"\n\n\n+", "\n\n", cleaned_text)
        
        return cleaned_text.strip()

class SectionDetector:
    def __init__(self):
        # Positive signals
        self.numbered_heading_pattern = r"^\d+(\.\d+)*\.?\s+[A-Z]"
        self.uppercase_heading_pattern = r"^[A-Z\s]{5,}$"
        
        # Negative signals
        self.currency_pattern = r"^£?\d+(\.\d{2})?$"
        self.rate_pattern = r"^\d+(\.\d+)?%\s+EAR$"
        self.generic_words = {"Yes", "No", "Note"}

    def is_heading(self, line: str) -> bool:
        line = line.strip()
        if not line:
            return False
        
        # Check negative signals first
        if re.match(self.currency_pattern, line) or re.match(self.rate_pattern, line):
            return False
        if line in self.generic_words:
            return False
        
        # Check positive signals
        if re.match(self.numbered_heading_pattern, line):
            return True
        if re.match(self.uppercase_heading_pattern, line):
            # Check length to avoid long sentences that happen to be uppercase
            if len(line) < 80:
                return True
                
        return False

class SectionAwareChunker:
    def __init__(self, max_chars: int = 1000, overlap_chars: int = 200):
        self.max_chars = max_chars
        self.overlap_chars = overlap_chars
        self.cleaner = TextCleaner()
        self.detector = SectionDetector()

    def chunk(self, doc: ExtractedDocument, citation_label: Optional[str] = None) -> List[Chunk]:
        citation_label = citation_label or doc.citation_label or "Unknown Source"
        
        # 1. Clean the full text
        full_raw_text = doc.full_text
        cleaned_text = self.cleaner.clean(full_raw_text)
        
        # 2. Map pages to cleaned text offsets (Best effort)
        # We'll use the raw text chunks per page and find them in cleaned text
        page_offsets = []
        current_cleaned_pos = 0
        for page in doc.pages:
            cleaned_page_text = self.cleaner.clean(page.text)
            if not cleaned_page_text:
                page_offsets.append((page.page_number, -1, -1))
                continue
            
            # Find this cleaned page text in the full cleaned text
            # This is a bit simplistic but works for mostly sequential text
            start_pos = cleaned_text.find(cleaned_page_text, current_cleaned_pos)
            if start_pos != -1:
                end_pos = start_pos + len(cleaned_page_text)
                page_offsets.append((page.page_number, start_pos, end_pos))
                current_cleaned_pos = end_pos
            else:
                page_offsets.append((page.page_number, -1, -1))

        # 3. Detect sections and chunk
        chunks: List[Chunk] = []
        lines = cleaned_text.split("\n")
        
        current_section_heading = None
        section_text = ""
        section_start_offset = 0
        
        # To simplify, we'll group lines into sections first
        sections = []
        current_section_content = []
        current_section_start = 0
        
        pos = 0
        for line in lines:
            line_len = len(line) + 1 # +1 for newline
            if self.detector.is_heading(line):
                # Save previous section
                if current_section_content:
                    sections.append({
                        "heading": current_section_heading,
                        "text": "\n".join(current_section_content),
                        "start_offset": current_section_start
                    })
                current_section_heading = line
                current_section_content = [line]
                current_section_start = pos
            else:
                current_section_content.append(line)
            pos += line_len
            
        # Add last section
        if current_section_content:
            sections.append({
                "heading": current_section_heading,
                "text": "\n".join(current_section_content),
                "start_offset": current_section_start
            })

        chunk_index = 1
        for section in sections:
            sect_text = section["text"]
            sect_heading = section["heading"]
            sect_start = section["start_offset"]
            
            if not sect_text.strip():
                continue
            
            # Internal chunking within section
            sect_pos = 0
            while sect_pos < len(sect_text):
                chunk_end = min(sect_pos + self.max_chars, len(sect_text))
                
                # Try to find a good break point (newline or space)
                if chunk_end < len(sect_text):
                    last_newline = sect_text.rfind("\n", sect_pos, chunk_end)
                    if last_newline != -1 and last_newline > sect_pos + (self.max_chars // 2):
                        chunk_end = last_newline
                    else:
                        last_space = sect_text.rfind(" ", sect_pos, chunk_end)
                        if last_space != -1 and last_space > sect_pos + (self.max_chars // 2):
                            chunk_end = last_space

                chunk_text = sect_text[sect_pos:chunk_end].strip()
                if chunk_text:
                    char_start = sect_start + sect_pos
                    char_end = sect_start + chunk_end
                    
                    # Determine page number
                    page_start = None
                    for p_num, p_start, p_end in page_offsets:
                        if p_start != -1 and char_start >= p_start and char_start < p_end:
                            page_start = p_num
                            break
                    
                    page_end = None
                    for p_num, p_start, p_end in page_offsets:
                        if p_start != -1 and char_end > p_start and char_end <= p_end:
                            page_end = p_num
                            break

                    chunk_hash = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()
                    chunk_id = f"{doc.source_id}::chunk::{chunk_index:04d}"
                    
                    chunks.append(Chunk(
                        chunk_id=chunk_id,
                        source_id=doc.source_id,
                        citation_label=citation_label,
                        title=doc.title,
                        document_type=doc.document_type,
                        product_area=doc.product_area,
                        section_heading=sect_heading,
                        chunk_index=chunk_index,
                        text=chunk_text,
                        character_start=char_start,
                        character_end=char_end,
                        page_number_start=page_start,
                        page_number_end=page_end,
                        chunk_hash=chunk_hash
                    ))
                    chunk_index += 1
                
                # Move position, accounting for overlap
                sect_pos = chunk_end - self.overlap_chars if chunk_end < len(sect_text) else len(sect_text)
                if sect_pos <= 0 and self.overlap_chars > 0: # Safety
                    sect_pos = chunk_end

        return chunks
