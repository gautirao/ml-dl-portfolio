from pathlib import Path

def is_safe_relative_path(path_str: str) -> bool:
    """
    Check if a path string is relative and doesn't contain traversal (..).
    """
    path = Path(path_str)
    if path.is_absolute():
        return False
    if ".." in path.parts:
        return False
    return True

def validate_path_prefix(path_str: str, allowed_prefixes: list[str]) -> bool:
    """
    Check if a path starts with one of the allowed prefixes.
    """
    return any(path_str.startswith(prefix) for prefix in allowed_prefixes)
