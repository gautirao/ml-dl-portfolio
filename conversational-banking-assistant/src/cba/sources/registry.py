from datetime import date
from pathlib import Path

import yaml

from cba.common.hashing import calculate_file_sha256
from cba.domain.enums import IntegrityStatus
from cba.domain.models import Source


class SourceRegistry:
    @staticmethod
    def load_from_yaml(file_path: Path) -> list[Source]:
        with open(file_path) as f:
            data = yaml.safe_load(f)
        
        if not data:
            return []
            
        return [Source(**item) for item in data]

    @staticmethod
    def verify_integrity(source: Source, project_root: Path) -> IntegrityStatus:
        # local_path is relative to project root (or data/raw/ as per design)
        # However, for tests, we allow it to be relative to the provided project_root
        full_path = project_root / source.local_path
        
        if not full_path.exists():
            return IntegrityStatus.MISSING_FILE
        
        actual_hash = calculate_file_sha256(full_path)
        if actual_hash != source.content_hash:
            return IntegrityStatus.HASH_MISMATCH
            
        return IntegrityStatus.OK

    @staticmethod
    def is_stale(source: Source) -> bool:
        today = date.today()
        days_since_retrieval = (today - source.retrieved_at).days
        return days_since_retrieval > source.freshness_threshold_days
