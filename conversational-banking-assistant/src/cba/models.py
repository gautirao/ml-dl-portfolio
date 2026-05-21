from pathlib import Path
from enum import Enum
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field, model_validator, field_validator
import re

class SourceType(str, Enum):
    PUBLIC_WEB = "public_web"
    PUBLIC_PDF = "public_pdf"

class ProductArea(str, Enum):
    CURRENT_ACCOUNTS = "current_accounts"
    OVERDRAFTS = "overdrafts"
    SAVINGS = "savings"
    CREDIT_CARDS = "credit_cards"

class DocumentType(str, Enum):
    TERMS_CONDITIONS = "terms_conditions"
    FEE_INFORMATION = "fee_information"
    OVERDRAFT_GUIDANCE = "overdraft_guidance"
    COMPLAINTS_PROCESS = "complaints_process"
    DEPOSIT_PROTECTION = "deposit_protection"
    PRIVACY_POLICY = "privacy_policy"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class StalePolicy(str, Enum):
    WARN_ONLY = "warn_only"
    BLOCK_ANSWER = "block_answer"
    REQUIRE_REFRESH = "require_refresh"

class ExtractionMethod(str, Enum):
    PYPDF = "pypdf"
    BEAUTIFULSOUP = "beautifulsoup"
    MANUAL_MARKDOWN = "manual_markdown"

class Source(BaseModel):
    source_id: str
    bank: str
    title: str
    source_type: SourceType
    product_area: ProductArea
    document_type: DocumentType
    url: str
    citation_label: str
    retrieved_at: date
    local_path: str
    content_hash: str
    content_hash_algorithm: str = "sha256"
    freshness_threshold_days: int
    allowed_for_demo: bool
    risk_level: RiskLevel
    financial_advice_boundary: Optional[str] = None
    stale_policy: StalePolicy
    licence_notes: Optional[str] = None
    extraction_method: Optional[ExtractionMethod] = None

    @field_validator("source_id")
    @classmethod
    def validate_source_id_format(cls, v: str) -> str:
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError("source_id must be lowercase kebab-case")
        return v

    @field_validator("local_path")
    @classmethod
    def validate_local_path_safety(cls, v: str) -> str:
        path = Path(v)
        if path.is_absolute():
            raise ValueError("absolute paths are not permitted in local_path")
        
        if ".." in path.parts:
            raise ValueError("Path traversal (..) is not permitted in local_path")

        # In a real scenario, we'd enforce data/raw/ prefix here.
        # However, to support tests using fixtures, we allow 'tests/fixtures/' as well.
        if not (v.startswith("data/raw/") or v.startswith("tests/fixtures/")):
            raise ValueError("local_path must be under data/raw/ (or tests/fixtures/ for testing)")
            
        return v

    @model_validator(mode="after")
    def validate_risk_constraints(self) -> "Source":
        # Risk/Boundary: If risk_level == "high", financial_advice_boundary must be non-empty.
        if self.risk_level == RiskLevel.HIGH and not self.financial_advice_boundary:
            raise ValueError("financial_advice_boundary is mandatory if risk_level is high")
        
        # Risk/Type: document_type in [fee_information, overdraft_guidance, complaints_process]
        # OR product_area == credit_cards
        # These must not allow risk_level = low.
        high_risk_types = [
            DocumentType.FEE_INFORMATION,
            DocumentType.OVERDRAFT_GUIDANCE,
            DocumentType.COMPLAINTS_PROCESS
        ]
        if (self.document_type in high_risk_types or self.product_area == ProductArea.CREDIT_CARDS) and self.risk_level == RiskLevel.LOW:
            raise ValueError(f"risk_level cannot be low for {self.document_type} or {self.product_area}")
            
        return self

    @model_validator(mode="after")
    def validate_demo_readiness(self) -> "Source":
        if self.allowed_for_demo:
            if not self.licence_notes:
                raise ValueError("licence_notes required if allowed_for_demo is True")
            if not self.citation_label:
                raise ValueError("citation_label required if allowed_for_demo is True")
            if self.url == "PLACEHOLDER_URL":
                raise ValueError("url cannot be PLACEHOLDER_URL if allowed_for_demo is True")
        return self

class ExtractedPage(BaseModel):
    page_number: int
    text: str

class ExtractedDocument(BaseModel):
    source_id: str
    citation_label: Optional[str] = None
    title: str
    document_type: DocumentType
    product_area: ProductArea
    local_path: str
    extracted_at: datetime
    pages: List[ExtractedPage]
    
    @property
    def full_text(self) -> str:
        return "\n\n".join([page.text for page in self.pages])

class Chunk(BaseModel):
    chunk_id: str
    source_id: str
    citation_label: str
    title: str
    document_type: DocumentType
    product_area: ProductArea
    section_heading: Optional[str] = None
    chunk_index: int
    text: str
    character_start: int
    character_end: int
    page_number_start: Optional[int] = None
    page_number_end: Optional[int] = None
    chunk_hash: str
