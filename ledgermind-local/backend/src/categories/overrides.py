import uuid
from typing import Optional, List, Dict, Any
from src.database.connection import db_manager

def create_transaction_override(
    transaction_id: str,
    new_category: str,
    new_subcategory: Optional[str] = None,
    reason: Optional[str] = None
) -> str:
    conn = db_manager.get_connection()
    
    # Get original category
    res = conn.execute(
        "SELECT category FROM transactions WHERE id = ?",
        (transaction_id,)
    ).fetchone()
    
    if not res:
        raise ValueError(f"Transaction {transaction_id} not found")
        
    original_category = res[0]
    override_id = str(uuid.uuid4())
    
    # Check if override already exists for this transaction
    # Requirements say we handle overrides. If one exists, we could either update it or keep a history.
    # The requirement says GET /api/transactions/{transaction_id}/category-history
    # This suggests we might want to keep multiple overrides, but usually the "latest" is effective.
    # However, for simplicity and typical UX, one active override per transaction is common.
    # Let's check if we should delete previous ones or just add to history.
    # Requirement 1 says table transaction_category_overrides.
    # I'll just insert a new one. The query for "effective_category" will pick the latest.
    
    conn.execute(
        """
        INSERT INTO transaction_category_overrides (
            id, transaction_id, original_category, new_category, new_subcategory, reason
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (override_id, transaction_id, original_category, new_category, new_subcategory, reason)
    )
    
    db_manager.log_event(
        "transaction_category_override_created",
        f"Category override created for transaction {transaction_id}",
        {
            "transaction_id": transaction_id,
            "new_category": new_category,
            "new_subcategory": new_subcategory,
            "reason": reason
        }
    )
    
    return override_id

def delete_transaction_override(transaction_id: str):
    conn = db_manager.get_connection()
    
    # Instead of deleting all, maybe we just delete the latest or clear all for this transaction?
    # "DELETE /api/transactions/{transaction_id}/category-override" implies removing the override effect.
    # I'll delete all overrides for this transaction to restore to original.
    
    conn.execute(
        "DELETE FROM transaction_category_overrides WHERE transaction_id = ?",
        (transaction_id,)
    )
    
    db_manager.log_event(
        "transaction_category_override_removed",
        f"Category overrides removed for transaction {transaction_id}",
        {"transaction_id": transaction_id}
    )

def get_transaction_override_history(transaction_id: str) -> List[Dict[str, Any]]:
    conn = db_manager.get_connection()
    
    res = conn.execute(
        """
        SELECT id, original_category, new_category, new_subcategory, reason, created_at
        FROM transaction_category_overrides
        WHERE transaction_id = ?
        ORDER BY created_at DESC
        """,
        (transaction_id,)
    ).fetchall()
    
    return [
        {
            "id": str(r[0]),
            "original_category": r[1],
            "new_category": r[2],
            "new_subcategory": r[3],
            "reason": r[4],
            "created_at": r[5]
        }
        for r in res
    ]
