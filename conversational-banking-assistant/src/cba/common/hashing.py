import hashlib
from pathlib import Path


def calculate_file_sha256(file_path: Path) -> str:
    """
    Calculate the SHA256 hash of a file.
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def calculate_text_sha256(text: str) -> str:
    """
    Calculate the SHA256 hash of a text string.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
