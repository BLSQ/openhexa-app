import posixpath


def is_safe_path(path: str) -> bool:
    normalized = posixpath.normpath(path)
    return not normalized.startswith("/") and not normalized.startswith("..")
