import logging
from src.database.connection import db_manager

logger = logging.getLogger(__name__)

class RuleService:
    @staticmethod
    def apply_rules() -> int:
        """Apply all merchant_rules to uncategorized transactions."""
        conn = db_manager.get_connection()
        rules = conn.execute("SELECT pattern, merchant_name, category, subcategory FROM merchant_rules").fetchall()
        
        total_updated = 0
        for pattern, merchant_name, category, subcategory in rules:
            # Check if pattern already has wildcards, if not, add them for broader matching if desired
            # But for Milestone 8, we'll stick to exact-ish match (ILIKE)
            search_pattern = pattern if '%' in pattern else f"%{pattern}%"
            
            res = conn.execute(
                """UPDATE transactions 
                   SET merchant = ?, category = ?, subcategory = ? 
                   WHERE (description ILIKE ? OR merchant ILIKE ?) 
                   AND (category IS NULL OR category = '' OR category = 'Uncategorized')
                   RETURNING id""",
                (merchant_name, category, subcategory, search_pattern, search_pattern)
            ).fetchall()
            total_updated += len(res)
        
        if total_updated > 0:
            db_manager.log_event("rules_applied", f"Applied rules to {total_updated} transactions", {"rules_count": len(rules)})
        
        return total_updated
