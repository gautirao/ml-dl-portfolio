# ADR-005: Human-in-the-Loop Categorization

## Status
Accepted

## Context
Automated categorization is often wrong or inconsistent. Merchants like "TESCO STORES 1234" and "TESCO EXPRESS" should be normalized to "Tesco" and assigned a consistent category.

## Decision
We will implement a **Human-in-the-Loop** workflow for categorization.
1.  **AI Suggestions:** When new merchants are encountered, the AI suggests a normalized name and category based on semantic similarity to existing data.
2.  **Review Queue:** Suggestions are placed in a "Review" state and do not affect deterministic reporting until approved.
3.  **User Approval:** The user reviews, edits, and approves suggestions.
4.  **Persistent Rules:** Once approved, these become "Golden Rules" in the database that are automatically applied to all future imports.

## Consequences
-   **Pros:** High data quality; consistent reporting over time; user control over categorization logic.
-   **Cons:** Requires user effort to clear the review queue; initial setup (categorizing the first few months) can be tedious.
