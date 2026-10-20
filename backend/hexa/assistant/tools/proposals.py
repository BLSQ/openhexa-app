"""Helpers shared by the tools that stage file changes for the user to review."""

from hexa.assistant.models import Conversation, ToolInvocation
from hexa.core.text_files import TextFiles


def pending_proposal(
    conversation: Conversation | None, tool_name: str
) -> ToolInvocation | None:
    """The latest successful proposal of `tool_name` still awaiting the user's decision."""
    if conversation is None:
        return None
    return (
        ToolInvocation.objects.filter(
            message__conversation=conversation,
            tool_name=tool_name,
            success=True,
            proposal_pending=True,
        )
        .order_by("-created_at")
        .first()
    )


def working_files(
    files: TextFiles, conversation: Conversation | None, tool_name: str
) -> TextFiles:
    """`files` as the agent works on them: seen through the pending proposal of
    `tool_name`, if there is one, so reads match what the next proposal builds on.
    """
    pending = pending_proposal(conversation, tool_name)
    if pending is None or not pending.tool_output:
        return files
    proposed = pending.tool_output
    return files.with_changes(
        {f["path"]: f["content"] for f in proposed.get("files", [])},
        proposed.get("deleted_paths", []),
    )


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


def nothing_to_delete_error(paths: list[str]) -> dict:
    listed = ", ".join(f"'{p}'" for p in paths)
    return {
        "error": (
            f"Nothing to delete for: {listed}. Use exact file paths or directory "
            "paths from the file list."
        )
    }
