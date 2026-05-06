import pandas as pd
from typing import List, Dict, Any, Optional
from .base import BaseAdapter
import uuid
import json
import re

class HSBCMinimalAdapter(BaseAdapter):
    @property
    def bank_name(self) -> str:
        return "HSBC"

    def can_parse(self, df: pd.DataFrame, headers: List[str], source_bank_override: Optional[str] = None) -> bool:
        if source_bank_override == "hsbc":
            return True
        
        # Check if 3 columns and look like date, description, amount
        if len(df.columns) == 3:
            # Try to see if first col is date and third is numeric
            try:
                first_val = str(df.iloc[0, 0])
                # Check for common date patterns (DD/MM/YYYY)
                if re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', first_val):
                    float(df.iloc[0, 2])
                    return True
            except:
                pass
        
        # Check for headers Date, Description, Amount
        hsbc_headers = {"Date", "Description", "Amount"}
        if hsbc_headers.issubset(set(headers)):
            return True
            
        return False

    def normalise(self, df: pd.DataFrame, source_file_id: str, account_name: Optional[str] = None) -> pd.DataFrame:
        # If no headers, rename columns
        if not any(h in df.columns for h in ["Date", "Description", "Amount"]):
            df.columns = ["Date", "Description", "Amount"]

        normalised_rows = []
        for _, row in df.iterrows():
            try:
                raw_amount = row.get("Amount")
                amount = float(raw_amount) if raw_amount is not None else 0.0
            except (ValueError, TypeError):
                amount = 0.0
            direction = "inflow" if amount > 0 else "outflow"
            
            description = str(row.get("Description", "")).strip()
            # Simple merchant derivation: first word or until some delimiter
            merchant = description.split("  ")[0].strip() if "  " in description else description
            
            canonical_row = {
                "id": str(uuid.uuid4()),
                "source_bank": self.bank_name,
                "source_file_id": source_file_id,
                "account_name": account_name or "HSBC Account",
                "transaction_date": pd.to_datetime(row.get("Date"), dayfirst=True).date() if "Date" in row else None,
                "posted_date": None,
                "description": description,
                "merchant": merchant,
                "amount": amount,
                "currency": "GBP",
                "direction": direction,
                "category": "Uncategorised",
                "subcategory": None,
                "balance": None,
                "reference": None,
                "raw_row_json": json.dumps(row.to_dict()),
                "created_at": pd.Timestamp.now()
            }
            
            canonical_row["transaction_fingerprint"] = self.get_fingerprint(canonical_row)
            normalised_rows.append(canonical_row)
            
        return pd.DataFrame(normalised_rows)
