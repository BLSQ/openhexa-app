import posixpath


def is_safe_path(path: str) -> bool:
    if "\x00" in path or "~" in path:
        return False
    normalized = posixpath.normpath(path)
    if normalized.startswith("/"):
        return False
    parts = normalized.split("/")
    return ".." not in parts
