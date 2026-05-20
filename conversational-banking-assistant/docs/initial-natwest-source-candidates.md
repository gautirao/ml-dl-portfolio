# Initial NatWest Source Candidates

## Overview
This document identifies the first set of candidate public banking-policy documents for NatWest. It prioritizes landing pages as canonical sources and marks direct PDF links as unverified to ensure system integrity. Risk levels and document types have been updated to align with the registry design schema (#4).

## Validation Note
**Any candidate with `url = PLACEHOLDER_URL`, a broken URL, or a `verification_status = candidate_unverified` MUST NOT be used for ingestion or evaluation until direct access and content integrity are verified in a subsequent task.**

**Verification status applies to the exact URL recorded in the table. A canonical landing page being accessible does not automatically verify all direct PDF/download targets.**

## Candidate Source List

| proposed source_id | bank | title | source_type | product_area | document_type | public URL (Download Target) | canonical URL (Landing Page) | risk_level | stale_policy | freshness_threshold_days | extraction_method | suitable_for_demo | verification_status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `nw-ca-terms-2026` | natwest | Your Current Account Terms | `public_pdf` | `current_accounts` | `terms_conditions` | [PDF](https://www.natwest.com/content/dam/natwest/personal/current-accounts/documents/nw-personal-current-account-terms.pdf) | [NatWest Terms Page](https://www.natwest.com/current-accounts/terms-and-conditions.html) | `high` | `block_answer` | 180 | `pypdf` | `true` | `candidate_unverified` |
| `nw-select-fid-2026` | natwest | Select Account Fee Information Document | `public_pdf` | `current_accounts` | `fee_information` | [PDF](https://www.natwest.com/content/dam/natwest/personal/current-accounts/documents/nw-select-fee-information-document.pdf) | [NatWest Terms Page](https://www.natwest.com/current-accounts/terms-and-conditions.html) | `medium` | `block_answer` | 180 | `pypdf` | `true` | `candidate_unverified` |
| `nw-reward-fid-2026` | natwest | Reward Account Fee Information Document | `public_pdf` | `current_accounts` | `fee_information` | [PDF](https://www.natwest.com/content/dam/natwest/personal/current-accounts/documents/nw-reward-fee-information-document.pdf) | [NatWest Terms Page](https://www.natwest.com/current-accounts/terms-and-conditions.html) | `medium` | `block_answer` | 180 | `pypdf` | `true` | `candidate_unverified` |
| `nw-od-guidance-2026` | natwest | Overdrafts & Cost Calculator Guidance | `public_web` | `overdrafts` | `overdraft_guidance` | [Web](https://www.natwest.com/current-accounts/overdrafts.html) | [NatWest Overdrafts](https://www.natwest.com/current-accounts/overdrafts.html) | `high` | `require_refresh` | 90 | `beautifulsoup` | `true` | `candidate_unverified` |
| `nw-complaints-2026` | natwest | How to make a complaint | `public_web` | `current_accounts` | `complaints_process` | [Web](https://www.natwest.com/support-centre/make-a-complaint.html) | [NatWest Support Centre](https://www.natwest.com/support-centre.html) | `high` | `require_refresh` | 180 | `beautifulsoup` | `true` | `candidate_unverified` |
| `nw-fscs-info-2026` | natwest | FSCS Information Sheet | `public_pdf` | `current_accounts` | `deposit_protection` | [PDF](https://www.natwest.com/content/dam/natwest/personal/security-centre/documents/fscs-information-sheet.pdf) | [NatWest FSCS Page](https://www.natwest.com/personal/security-centre/protecting-your-money/fscs.html) | `medium` | `block_answer` | 365 | `pypdf` | `true` | `candidate_unverified` |
| `nw-privacy-2026` | natwest | Privacy Policy | `public_web` | `current_accounts` | `privacy_policy` | [Web](https://www.natwest.com/privacy.html) | [NatWest Privacy Landing](https://www.natwest.com/privacy.html) | `medium` | `warn_only` | 365 | `beautifulsoup` | `true` | `candidate_unverified` |

*Note: For `nw-ca-terms-2026`, `nw-select-fid-2026`, and `nw-reward-fid-2026`, the direct PDF download URLs are currently `candidate_unverified`. However, the canonical NatWest rates-and-charges landing page has visible download links for the current account terms and fee information documents.*

## Detailed Metadata Analysis

*   **Why Useful:**
    *   `nw-ca-terms-2026`: Primary legal framework for customer relationship.
    *   `nw-select/reward-fid-2026`: Standardized pricing for comparison and fee advice.
    *   `nw-od-guidance-2026`: Critical for borrowing cost explanations and regulatory compliance.
    *   `nw-complaints-2026`: Ensures the assistant can guide users through formal resolution steps.
    *   `nw-fscs-info-2026`: Provides trust and safety information regarding deposit guarantees.
    *   `nw-privacy-2026`: Governs data use and transparency, essential for AI governance.

*   **Licence/Copyright Note:** Standard NatWest Copyright. Documents are public transparency items. Suitable for demo/academic use under fair dealing for research.

*   **Financial Advice Boundary (Required for High Risk):**
    *   The assistant must strictly explain fees, terms, and processes.
    *   It **must not** recommend specific products or borrowing amounts based on personal financial circumstances.

## Risks & Mitigations
1.  **Unverified PDF Links:** Direct links to `.../documents/*.pdf` are frequently updated by banks, leading to 404 errors.
    *   *Mitigation:* Task #5 output explicitly lists these as `candidate_unverified`. Landing pages are used as canonical anchors for future automated discovery.
2.  **Incorrect Risk Assessment:** Providing wrong fee info is a high-impact failure.
    *   *Mitigation:* Set `risk_level: high` and `stale_policy: block_answer` for cost-sensitive documents.
3.  **Extraction Methodology:** PDF structures (especially FIDs) vary.
    *   *Mitigation:* Recommended `pypdf` or `manual_markdown` for complex tables to ensure high-fidelity ingestion.