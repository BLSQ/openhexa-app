import posixpath


def is_safe_path(path: str, allow_tilde: bool = False) -> bool:
    if "\x00" in path or ("~" in path and not allow_tilde):
        return False
    normalized = posixpath.normpath(path)
    if normalized.startswith("/"):
        return False
    parts = normalized.split("/")
    return ".." not in parts
