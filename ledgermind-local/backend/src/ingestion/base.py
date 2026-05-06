from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import pandas as pd
import hashlib
import json

class BaseAdapter(ABC):
    @property
    @abstractmethod
    def bank_name(self) -> str:
        pass

    @abstractmethod
    def can_parse(self, df: pd.DataFrame, headers: List[str], source_bank_override: Optional[str] = None) -> bool:
        pass

    @abstractmethod
    def normalise(self, df: pd.DataFrame, source_file_id: str, account_name: Optional[str] = None) -> pd.DataFrame:
        pass

    def get_fingerprint(self, row: Dict[str, Any]) -> str:
        # Stable fields for fingerprinting
        components = [
            str(self.bank_name),
            str(row.get("transaction_date")),
            str(row.get("amount")),
            str(row.get("description") or "").strip(),
            str(row.get("reference") or "").strip(),
            str(row.get("balance") or "")
        ]
        raw_str = "|".join(components)
        return hashlib.sha256(raw_str.encode()).hexdigest()

    def get_preview_mapping(self) -> Dict[str, str]:
        return {
            "transaction_date": "Date",
            "description": "Description",
            "amount": "Amount",
            "direction": "Inflow/Outflow"
        }
