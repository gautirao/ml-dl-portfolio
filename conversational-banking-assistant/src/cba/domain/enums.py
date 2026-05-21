from enum import Enum

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

class IntegrityStatus(str, Enum):
    OK = "OK"
    MISSING_FILE = "MISSING_FILE"
    HASH_MISMATCH = "HASH_MISMATCH"
