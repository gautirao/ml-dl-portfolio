import pandas as pd
from typing import List, Optional, Tuple
from .base import BaseAdapter
from .monzo import MonzoAdapter
from .hsbc_minimal import HSBCMinimalAdapter

class IngestionDetector:
    def __init__(self):
        self.adapters: List[BaseAdapter] = [
            MonzoAdapter(),
            HSBCMinimalAdapter()
        ]

    def detect(self, df: pd.DataFrame, headers: List[str], source_bank_override: Optional[str] = None) -> Tuple[Optional[BaseAdapter], float]:
        # source_bank_override can be 'auto', 'monzo', 'hsbc'
        if source_bank_override == 'auto':
            source_bank_override = None

        best_adapter = None
        for adapter in self.adapters:
            if adapter.can_parse(df, headers, source_bank_override):
                return adapter, 1.0 # Simple confidence for now
        
        return None, 0.0
