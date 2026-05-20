# Public Banking Source Registry Design

**Status:** Draft / Approved Design  
**Associated Issue:** #4 Design public banking source registry schema

## 📖 Overview
The **Source Registry** is a foundational component of the Conversational Banking Assistant. It serves as the "Source of Truth" for all documents ingested into the RAG system, ensuring that every answer is grounded in verified, auditable, and fresh public banking policy documentation.

## 🏗️ Folder Layout
```text
conversational-banking-assistant/
├── data/
│   ├── registry/           # Source registry definitions
│   │   └── sources.yaml    # The main registry file
│   ├── raw/                # Original downloads (PDF/HTML) - [STRICTLY GITIGNORED]
│   ├── processed/          # Cleaned text/markdown chunks - [STRICTLY GITIGNORED]
│   └── vector_store/       # Local database files - [STRICTLY GITIGNORED]
├── docs/
│   ├── source-registry-design.md # This design specification
│   └── safety-policy.md    # Domain-specific refusal rules
```

## 📋 Schema Definition

### Identity & Metadata (Required)
- `source_id`: (string) Lowercase kebab-case, globally unique. Format: `{bank}-{product}-{doc-type}-{year/v}`.
- `bank`: (string) e.g., `natwest`, `generic_bank`.
- `title`: (string) Official name of the document.
- `source_type`: (enum) `public_web`, `public_pdf`.
- `product_area`: (enum) `current_accounts`, `overdrafts`, `savings`, `credit_cards`.
- `document_type`: (enum) `terms_conditions`, `fee_information`, `overdraft_guidance`, `complaints_process`.
- `url`: (string) The source URL.
- `citation_label`: (string) Short name for citations (e.g., `[NatWest-Fees-26]`).

### Technical & Versioning (Required)
- `retrieved_at`: (iso-date) `YYYY-MM-DD`.
- `local_path`: (string) Relative path under `data/raw/`. No absolute paths or `../`.
- `content_hash`: (string) Hash of the local file.
- `content_hash_algorithm`: (string) Default: `sha256`.
- `freshness_threshold_days`: (int) Days before the source is considered stale.
- `allowed_for_demo`: (boolean) Flag for portfolio visibility.

### Governance & Safety (Required/Conditional)
- `risk_level`: (enum) `low`, `medium`, `high`.
- `financial_advice_boundary`: (string) **Mandatory if `risk_level` is `high`**.
- `stale_policy`: (enum) `warn_only`, `block_answer`, `require_refresh`.
  - **Rule:** `fee_information`, `overdraft_guidance`, `credit_cards`, and `complaints_process` documents should not use `warn_only` unless explicitly justified.

### Additional Governance Fields (Optional/Extended)
- `last_verified_at`: (iso-date) Last check for URL/content availability.
- `expected_update_frequency`: (enum) `monthly`, `quarterly`, `annually`, `ad_hoc`.
- `extraction_method`: (enum) `pypdf`, `beautifulsoup`, `manual_markdown`.
- `licence_notes`: (string) Note on document usage terms. **Mandatory if `allowed_for_demo` is true**.
- `source_owner`: (string) Dept/Entity responsible for the source (e.g., `NatWest Legal`).
- `access_type`: (enum) `public_unrestricted`, `public_subject_to_terms`.
- `language`: (string) e.g., `en-GB`.
- `jurisdiction`: (string) e.g., `UK`.

## 🛡️ Validation Rules

### Path & ID Rules
- `source_id` must be lowercase kebab-case.
- `local_path` must be relative and remain under `conversational-banking-assistant/data/raw/`.
- No absolute paths or parent directory traversal (`../`) are permitted.

### Safety & Risk Validation
- If `risk_level` is `high`, `financial_advice_boundary` is mandatory.
- If `document_type` is one of [`fee_information`, `overdraft_guidance`, `complaints_process`, `credit_cards`], `risk_level` **cannot** be `low`.
- If `allowed_for_demo` is true:
  - `licence_notes` and `citation_label` must be present.
  - `url` must not be `PLACEHOLDER_URL` (permitted only in planning/fixtures).

### Copyright & Licence Policy
- Source metadata and URLs are tracked in Git.
- Raw documents (`data/raw/`) **must** remain gitignored.
- Full bank documents are **never** republished in the repository.
- Use citations, links, and limited excerpts only.
- Verify source terms before using screenshots or excerpts in public demos.

## 📝 Example Registry Entries

```yaml
- source_id: natwest-current-accounts-fee-info-2026
  bank: natwest
  title: Personal Current Account Fee Information Document
  source_type: public_pdf
  product_area: current_accounts
  document_type: fee_information
  url: PLACEHOLDER_URL
  retrieved_at: YYYY-MM-DD
  local_path: data/raw/natwest/fees-2026.pdf
  content_hash: PLACEHOLDER_HASH
  content_hash_algorithm: sha256
  freshness_threshold_days: 180
  stale_policy: block_answer
  risk_level: medium
  allowed_for_demo: true
  licence_notes: "Public transparency document. Use excerpts for education only."
  citation_label: "[NatWest-Fees-26]"
  jurisdiction: UK
  language: en-GB

- source_id: natwest-personal-overdraft-guide-2026
  bank: natwest
  title: Your Guide to Overdrafts
  source_type: public_web
  product_area: overdrafts
  document_type: overdraft_guidance
  url: PLACEHOLDER_URL
  retrieved_at: YYYY-MM-DD
  local_path: data/raw/natwest/overdraft-guide.html
  content_hash: PLACEHOLDER_HASH
  content_hash_algorithm: sha256
  freshness_threshold_days: 90
  stale_policy: require_refresh
  risk_level: high
  financial_advice_boundary: "Do not provide personal borrowing recommendations; only explain fee structures."
  allowed_for_demo: true
  licence_notes: "Standard public web content. Citations only."
  citation_label: "[NatWest-OD-26]"
  extraction_method: beautifulsoup
```

## 🧪 Testing Strategy
Implementation of the registry loader (#6) must verify:
1.  **Schema Compliance:** Enums and mandatory fields.
2.  **Safety Constraints:** `financial_advice_boundary` presence for high-risk items.
3.  **Path Integrity:** Relative path constraints and directory isolation.
4.  **Demo Readiness:** URL and licence checks for demo-flagged items.
5.  **Hash Verification:** Local file integrity against registered hash.
