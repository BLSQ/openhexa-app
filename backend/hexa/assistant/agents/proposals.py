"""Helpers shared by the tools that stage file changes for the user to review."""

MAX_COMMIT_MESSAGE_LENGTH = 500


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


def resolve_commit_message(
    requested: str | None, pending_output: dict | None
) -> str | None:
    """The message the proposal should carry.

    A chained call that does not restate a message keeps the pending one, the same
    way unchanged files are preserved.
    """
    cleaned = (requested or "").strip()
    if cleaned:
        return cleaned
    return (pending_output or {}).get("commit_message")


def commit_message_error(requested: str | None) -> dict | None:
    """Reject a message too long to be the one-line summary the tools ask for."""
    length = len((requested or "").strip())
    if length <= MAX_COMMIT_MESSAGE_LENGTH:
        return None
    return {
        "error": (
            f"commit_message is {length} characters, the limit is "
            f"{MAX_COMMIT_MESSAGE_LENGTH}. Summarize the change in one line."
        )
    }


def nothing_to_delete_error(paths: list[str]) -> dict:
    listed = ", ".join(f"'{p}'" for p in paths)
    return {
        "error": (
            f"Nothing to delete for: {listed}. Use exact file paths or directory "
            "paths from the file list."
        )
    }
