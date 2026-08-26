"""Helpers shared by the tools that stage file changes for the user to review."""


def resolve_deleted_paths(
    requested: list[str], known_paths: set[str]
) -> tuple[set[str], list[str]]:
    """Expand each requested path into the concrete files it removes.

    A requested path is either a file, or a directory standing for everything under it.
    Returns the resolved file paths, plus every requested path that matched nothing —
    all of them rather than just the first, so the caller can report every bad path in
    one go instead of making the model retry once per mistake.
    """
    resolved: set[str] = set()
    unmatched: list[str] = []
    for path in requested:
        prefix = path.rstrip("/") + "/"
        matched = {p for p in known_paths if p == path or p.startswith(prefix)}
        if matched:
            resolved |= matched
        elif path not in unmatched:
            unmatched.append(path)
    return resolved, unmatched


def nothing_to_delete_error(paths: list[str]) -> dict:
    listed = ", ".join(f"'{p}'" for p in paths)
    return {
        "error": (
            f"Nothing to delete for: {listed}. Use exact file paths or directory "
            "paths from the file list."
        )
    }
