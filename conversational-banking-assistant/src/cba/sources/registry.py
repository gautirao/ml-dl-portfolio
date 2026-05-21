import yaml
import hashlib
from pathlib import Path
from typing import List, Optional
from datetime import date

from cba.domain.models import Source
from cba.domain.enums import IntegrityStatus

class SourceRegistry:
    @staticmethod
    def load_from_yaml(file_path: Path) -> List[Source]:
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        
        if not data:
            return []
            
        return [Source(**item) for item in data]

    @staticmethod
    def calculate_sha256(file_path: Path) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def verify_integrity(source: Source, project_root: Path) -> IntegrityStatus:
        # local_path is relative to project root (or data/raw/ as per design)
        # However, for tests, we allow it to be relative to the provided project_root
        full_path = project_root / source.local_path
        
        if not full_path.exists():
            return IntegrityStatus.MISSING_FILE
        
        actual_hash = SourceRegistry.calculate_sha256(full_path)
        if actual_hash != source.content_hash:
            return IntegrityStatus.HASH_MISMATCH
            
        return IntegrityStatus.OK

    @staticmethod
    def is_stale(source: Source) -> bool:
        today = date.today()
        days_since_retrieval = (today - source.retrieved_at).days
        return days_since_retrieval > source.freshness_threshold_days
