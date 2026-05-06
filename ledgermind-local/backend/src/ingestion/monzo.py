import pandas as pd
from typing import List, Dict, Any, Optional
from .base import BaseAdapter
import uuid
import json

class MonzoAdapter(BaseAdapter):
    @property
    def bank_name(self) -> str:
        return "MONZO"

    def can_parse(self, df: pd.DataFrame, headers: List[str], source_bank_override: Optional[str] = None) -> bool:
        if source_bank_override == "monzo":
            return True
        # Typical Monzo columns
        monzo_indicators = {"Transaction ID", "Amount", "Currency", "Name", "Description"}
        return monzo_indicators.issubset(set(headers))

    def normalise(self, df: pd.DataFrame, source_file_id: str, account_name: Optional[str] = None) -> pd.DataFrame:
        normalised_rows = []
        for _, row in df.iterrows():
            try:
                raw_amount = row.get("Amount")
                amount = float(raw_amount) if raw_amount is not None else 0.0
            except (ValueError, TypeError):
                amount = 0.0
            
            direction = "inflow" if amount > 0 else "outflow"
            
            # Map Monzo fields to canonical schema
            # Monzo "Name" is often the merchant, "Description" might have more detail
            merchant = str(row.get("Name", ""))
            description = str(row.get("Description", ""))
            
            canonical_row = {
                "id": str(uuid.uuid4()),
                "source_bank": self.bank_name,
                "source_file_id": source_file_id,
                "account_name": account_name or "Monzo Account",
                "transaction_date": pd.to_datetime(row.get("Date"), dayfirst=True).date() if "Date" in row else None,
                "posted_date": None, # Monzo usually has one date or timestamp
                "description": description or merchant,
                "merchant": merchant,
                "amount": amount,
                "currency": row.get("Currency", "GBP"),
                "direction": direction,
                "category": row.get("Category"),
                "subcategory": None,
                "balance": row.get("Balance"),
                "reference": row.get("Transaction ID"),
                "raw_row_json": json.dumps(row.to_dict()),
                "created_at": pd.Timestamp.now()
            }
            
            # Add fingerprint
            canonical_row["transaction_fingerprint"] = self.get_fingerprint(canonical_row)
            normalised_rows.append(canonical_row)
            
        return pd.DataFrame(normalised_rows)
