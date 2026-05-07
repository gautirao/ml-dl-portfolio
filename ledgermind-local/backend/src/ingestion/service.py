import pandas as pd
import io
import uuid
import json
import hashlib
from typing import Optional, Dict, Any, List, Tuple
from .detector import IngestionDetector
from ..database.connection import db_manager

class IngestionService:
    def __init__(self):
        self.detector = IngestionDetector()

    def _read_csv(self, filename: str, content: bytes) -> Tuple[pd.DataFrame, List[str]]:
        try:
            if filename.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(io.BytesIO(content))
                return df, list(df.columns)

            # First, try to detect if it has a header by looking at the first row
            # We use a small sample to avoid reading the whole file twice if possible
            sample = content[:2048].decode('utf-8', errors='ignore')
            
            # Simple heuristic: if the first row has many non-numeric strings and the second row has numbers, it's likely a header.
            # But Monzo has rich headers. HSBC minimal has Date, Description, Amount.
            
            # We'll try to read with header first.
            df = pd.read_csv(io.BytesIO(content))
            
            # If it's HSBC and the columns look like data (e.g. first col is a date-like string), 
            # then it probably DIDN'T have a header.
            first_col_name = str(df.columns[0])
            import re
            if re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', first_col_name) and len(df.columns) == 3:
                # Re-read without header
                df = pd.read_csv(io.BytesIO(content), header=None)
                return df, []
            
            return df, list(df.columns)
        except Exception as e:
            df = pd.read_csv(io.BytesIO(content), header=None)
            return df, []

    def preview(self, filename: str, content: bytes, source_bank_override: Optional[str] = None) -> Dict[str, Any]:
        df, headers = self._read_csv(filename, content)
        # Replace NaN with None for JSON compliance
        df = df.astype(object).where(pd.notnull(df), None)
        
        adapter, confidence = self.detector.detect(df, headers, source_bank_override)
        
        warnings = []
        if not adapter:
            warnings.append("Could not automatically detect bank format. Please select bank type manually.")
        
        # Log to audit_events
        conn = db_manager.get_connection()
        audit_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO audit_events (id, event_type, description, metadata) VALUES (?, ?, ?, ?)",
            (audit_id, "import_preview", f"Previewed {filename}", json.dumps({"filename": filename, "confidence": confidence}))
        )

        return {
            "filename": filename,
            "detected_bank": adapter.bank_name if adapter else "Unknown",
            "confidence": confidence,
            "headers": headers,
            "row_count": len(df),
            "preview_rows": df.head(5).to_dict(orient='records'),
            "proposed_mapping": adapter.get_preview_mapping() if adapter else {},
            "warnings": warnings
        }

    def process_import(self, filename: str, content: bytes, source_bank_override: Optional[str] = "auto", account_name: Optional[str] = None) -> Dict[str, Any]:
        df, headers = self._read_csv(filename, content)
        df = df.astype(object).where(pd.notnull(df), None)
        adapter, confidence = self.detector.detect(df, headers, source_bank_override)
        
        if not adapter:
            raise ValueError("Could not detect bank format and no valid override provided.")

        # Calculate file hash
        file_hash = hashlib.sha256(content).hexdigest()
        
        conn = db_manager.get_connection()
        
        # Check if file already uploaded
        existing_file = conn.execute("SELECT id, row_count FROM uploaded_files WHERE file_hash = ?", (file_hash,)).fetchone()
        if existing_file:
             # If file already exists, we skip the file insertion.
             # We might still want to check if all transactions are there, but for MVP we can return or proceed with skipped transactions.
             source_file_id = existing_file[0]
             # We won't re-insert uploaded_files, but we will proceed to check transactions.
        else:
            # 1. Insert uploaded_files
            source_file_id = str(uuid.uuid4())
            conn.execute(
                "INSERT INTO uploaded_files (id, filename, file_hash, bank_type, row_count) VALUES (?, ?, ?, ?, ?)",
                (source_file_id, filename, file_hash, adapter.bank_name, len(df))
            )
        
        # 2. Normalise
        normalised_df = adapter.normalise(df, source_file_id, account_name)
        
        # 3. Insert into transactions, skipping duplicates by fingerprint
        imported_count = 0
        skipped_count = 0
        
        # Get existing fingerprints for this bank to skip
        existing_fps = set(r[0] for r in conn.execute("SELECT transaction_fingerprint FROM transactions WHERE source_bank = ?", (adapter.bank_name,)).fetchall())
        
        # Track fingerprints seen in this import session to handle duplicates within the same file
        session_fps = {}

        for _, row in normalised_df.iterrows():
            fp = row['transaction_fingerprint']
            
            # If this fingerprint has been seen in this session, append a suffix
            if fp in session_fps:
                session_fps[fp] += 1
                fp = f"{fp}_{session_fps[fp]}"
            else:
                session_fps[fp] = 0
            
            if fp in existing_fps:
                skipped_count += 1
                continue
            
            conn.execute(
                """INSERT INTO transactions (
                    id, source_bank, source_file_id, account_name, transaction_date, 
                    description, merchant, amount, currency, direction, 
                    category, transaction_fingerprint, raw_row_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    row['id'], row['source_bank'], row['source_file_id'], row['account_name'], row['transaction_date'],
                    row['description'], row['merchant'], row['amount'], row['currency'], row['direction'],
                    row['category'], fp, row['raw_row_json']
                )
            )
            imported_count += 1

        # 4. Apply deterministic rules
        from ..categories.rules import RuleService
        RuleService.apply_rules()

        # Audit
        conn.execute(
            "INSERT INTO audit_events (id, event_type, description, metadata) VALUES (?, ?, ?, ?)",
            (str(uuid.uuid4()), "import_completed", f"Imported {filename}", json.dumps({"imported": imported_count, "skipped": skipped_count}))
        )

        # Summary info
        date_min = normalised_df['transaction_date'].min() if not normalised_df.empty else None
        date_max = normalised_df['transaction_date'].max() if not normalised_df.empty else None

        return {
            "detected_bank": adapter.bank_name,
            "filename": filename,
            "source_file_id": source_file_id,
            "row_count": len(df),
            "imported_count": imported_count,
            "skipped_count": skipped_count,
            "duplicate_count": skipped_count,
            "date_min": str(date_min),
            "date_max": str(date_max),
            "warnings": []
        }
