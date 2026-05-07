import uuid
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.database.connection import db_manager
from src.search.semantic_matcher import SemanticMatcher
from src.search.indexer import Indexer
from src.categories.rules import RuleService

class SuggestionService:
    def __init__(self, semantic_matcher: Optional[SemanticMatcher] = None, indexer: Optional[Indexer] = None):
        self.semantic_matcher = semantic_matcher
        self.indexer = indexer

    async def generate_suggestions(self, limit: int = 50) -> List[Dict[str, Any]]:
        # 0. Apply deterministic rules first
        RuleService.apply_rules()
        
        conn = db_manager.get_connection()
        
        # 1. Find transactions without category or with low confidence
        # We group by description/merchant to suggest rules for patterns
        query = """
        SELECT description, merchant, id
        FROM transactions
        WHERE category IS NULL OR category = '' OR category = 'Uncategorized'
        LIMIT ?
        """
        uncategorised = conn.execute(query, (limit,)).fetchall()
        
        suggestions = []
        for desc, merch, trans_id in uncategorised:
            merchant_text = merch or desc
            
            # Check if we already have a pending suggestion for this merchant_text
            existing = conn.execute(
                "SELECT id FROM category_suggestions WHERE merchant_text = ? AND status = 'pending'",
                (merchant_text,)
            ).fetchone()
            if existing:
                continue

            # Use semantic matcher if available
            suggested_merchant = None
            suggested_category = None
            suggested_subcategory = None
            confidence = 0.0
            evidence = {"method": "none"}
            
            if self.semantic_matcher:
                matches = await self.semantic_matcher.find_matches(merchant_text, limit=3)
                if matches:
                    # Filter out matches that are just the same merchant_text with no category
                    valid_matches = [m for m in matches if m.get("category")]
                    if valid_matches:
                        best_match = valid_matches[0]
                        # score 0 is perfect match in Chroma cosine distance (usually 0 to 2)
                        # We'll normalize roughly: 1.0 - (score/2.0)
                        confidence = max(0.0, 1.0 - (best_match["score"] / 2.0))
                        suggested_merchant = best_match.get("merchant")
                        suggested_category = best_match.get("category")
                        suggested_subcategory = best_match["metadata"].get("subcategory")
                        evidence = {
                            "method": "semantic_search",
                            "top_matches": valid_matches
                        }
            
            suggestion_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO category_suggestions (
                    id, transaction_id, merchant_text, suggested_merchant, 
                    suggested_category, suggested_subcategory, confidence, evidence_json, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    suggestion_id, trans_id, merchant_text, suggested_merchant,
                    suggested_category, suggested_subcategory, confidence, json.dumps(evidence), 'pending'
                )
            )
            
            suggestions.append({
                "id": suggestion_id,
                "transaction_id": trans_id,
                "merchant_text": merchant_text,
                "suggested_merchant": suggested_merchant,
                "suggested_category": suggested_category,
                "suggested_subcategory": suggested_subcategory,
                "confidence": confidence,
                "status": "pending"
            })
            
        # Log event
        db_manager.log_event(
            "category_suggestions_generated",
            f"Generated {len(suggestions)} suggestions",
            {"count": len(suggestions)}
        )
        
        return suggestions

    def get_suggestions(self, status: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        conn = db_manager.get_connection()
        query = "SELECT * FROM category_suggestions"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        results = conn.execute(query, params).df().to_dict(orient='records')
        for r in results:
            if r['evidence_json']:
                try:
                    r['evidence_json'] = json.loads(r['evidence_json'])
                except:
                    pass
        return results

    async def approve_suggestion(self, suggestion_id: str, apply_to_matching: bool = False) -> Dict[str, Any]:
        conn = db_manager.get_connection()
        
        res = conn.execute("SELECT * FROM category_suggestions WHERE id = ?", (suggestion_id,)).df().to_dict(orient='records')
        if not res:
            raise ValueError("Suggestion not found")
        
        s = res[0]
        
        # 1. Create/Update merchant_rule
        pattern = s['merchant_text']
        
        existing_rule = conn.execute("SELECT id FROM merchant_rules WHERE pattern = ?", (pattern,)).fetchone()
        if existing_rule:
            conn.execute(
                "UPDATE merchant_rules SET merchant_name = ?, category = ?, subcategory = ? WHERE pattern = ?",
                (s['suggested_merchant'], s['suggested_category'], s['suggested_subcategory'], pattern)
            )
        else:
            conn.execute(
                "INSERT INTO merchant_rules (id, pattern, merchant_name, category, subcategory) VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), pattern, s['suggested_merchant'], s['suggested_category'], s['suggested_subcategory'])
            )
        
        # 2. Mark suggestion as approved
        conn.execute(
            "UPDATE category_suggestions SET status = 'approved', reviewed_at = ? WHERE id = ?",
            (datetime.now(), suggestion_id)
        )
        
        # 3. Apply to matching transactions if requested
        updated_count = 0
        if apply_to_matching:
            conn.execute(
                "UPDATE transactions SET merchant = ?, category = ?, subcategory = ? WHERE (description ILIKE ? OR merchant ILIKE ?) AND (category IS NULL OR category = '' OR category = 'Uncategorized')",
                (s['suggested_merchant'], s['suggested_category'], s['suggested_subcategory'], pattern, pattern)
            )
            # Rough estimate of updated count for auditing
            updated_count = conn.execute("SELECT count(*) FROM transactions WHERE merchant = ? AND category = ? AND (description ILIKE ? OR merchant ILIKE ?)", 
                                         (s['suggested_merchant'], s['suggested_category'], pattern, pattern)).fetchone()[0]

        # 4. Trigger index rebuild/update if indexer exists
        if self.indexer:
            await self.indexer.rebuild_index()

        # Audit
        db_manager.log_event(
            "category_suggestion_approved",
            f"Approved suggestion for {pattern}",
            {"suggestion_id": suggestion_id, "updated_transactions": updated_count}
        )
        
        return {"status": "approved", "updated_transactions": updated_count}

    def reject_suggestion(self, suggestion_id: str) -> Dict[str, Any]:
        conn = db_manager.get_connection()
        conn.execute(
            "UPDATE category_suggestions SET status = 'rejected', reviewed_at = ? WHERE id = ?",
            (datetime.now(), suggestion_id)
        )
        db_manager.log_event("category_suggestion_rejected", f"Rejected suggestion {suggestion_id}")
        return {"status": "rejected"}

    async def edit_suggestion(self, suggestion_id: str, edited_data: Dict[str, Any], apply_to_matching: bool = False) -> Dict[str, Any]:
        conn = db_manager.get_connection()
        
        # Update suggestion with new values
        conn.execute(
            """UPDATE category_suggestions SET 
                suggested_merchant = ?, 
                suggested_category = ?, 
                suggested_subcategory = ?,
                status = 'edited',
                reviewed_at = ?
            WHERE id = ?""",
            (
                edited_data.get('suggested_merchant'),
                edited_data.get('suggested_category'),
                edited_data.get('suggested_subcategory'),
                datetime.now(),
                suggestion_id
            )
        )
        
        # Fetch updated suggestion to create rule
        res = conn.execute("SELECT * FROM category_suggestions WHERE id = ?", (suggestion_id,)).df().to_dict(orient='records')
        if not res:
            raise ValueError("Suggestion not found after update")
        s = res[0]
        
        # Create/Update merchant_rule
        pattern = s['merchant_text']
        existing_rule = conn.execute("SELECT id FROM merchant_rules WHERE pattern = ?", (pattern,)).fetchone()
        if existing_rule:
            conn.execute(
                "UPDATE merchant_rules SET merchant_name = ?, category = ?, subcategory = ? WHERE pattern = ?",
                (s['suggested_merchant'], s['suggested_category'], s['suggested_subcategory'], pattern)
            )
        else:
            conn.execute(
                "INSERT INTO merchant_rules (id, pattern, merchant_name, category, subcategory) VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), pattern, s['suggested_merchant'], s['suggested_category'], s['suggested_subcategory'])
            )
            
        updated_count = 0
        if apply_to_matching:
            conn.execute(
                "UPDATE transactions SET merchant = ?, category = ?, subcategory = ? WHERE (description ILIKE ? OR merchant ILIKE ?) AND (category IS NULL OR category = '' OR category = 'Uncategorized')",
                (s['suggested_merchant'], s['suggested_category'], s['suggested_subcategory'], pattern, pattern)
            )
            # Rough estimate of updated count for auditing
            updated_count = conn.execute("SELECT count(*) FROM transactions WHERE merchant = ? AND category = ? AND (description ILIKE ? OR merchant ILIKE ?)", 
                                         (s['suggested_merchant'], s['suggested_category'], pattern, pattern)).fetchone()[0]

        if self.indexer:
            await self.indexer.rebuild_index()

        db_manager.log_event(
            "category_suggestion_edited",
            f"Edited and approved suggestion for {pattern}",
            {"suggestion_id": suggestion_id, "updated_transactions": updated_count}
        )
        
        return {"status": "edited", "updated_transactions": updated_count}
