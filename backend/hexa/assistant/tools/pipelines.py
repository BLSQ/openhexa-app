import io
import zipfile

from pydantic import BaseModel

from hexa.assistant.models import Conversation
from hexa.assistant.tools.proposals import (
    nothing_to_delete_error,
    pending_proposal,
    resolve_commit_message,
    resolve_deleted_paths,
)
from hexa.pipelines.models import Pipeline


class ProposedFile(BaseModel):
    name: str
    content: str


def propose_pipeline_version(
    pipeline: Pipeline,
    modified_files: list[ProposedFile] | None = None,
    deleted_files: list[str] | None = None,
    commit_message: str | None = None,
    conversation: Conversation | None = None,
) -> dict:
    """Propose a new version of the pipeline.

    Always call this tool with the files you modified or created in modified_files.
    Each entry must have a 'name' (e.g. 'pipeline.py') and 'content' (the full file text).
    List any files to remove in deleted_files. A directory path removes everything under it.
    Deletions cover binary files too, even though their content is never inlined here.
    Unchanged files are preserved automatically.
    Pass commit_message to describe the change as a Conventional Commit: a
    `type(scope): summary` subject line, optionally followed by a blank line and a
    short body explaining why.
    It becomes the description of the version if the user accepts the proposal.
    """
    current_files: dict[str, str] = {}
    deleted_paths: set[str] = set()
    all_paths: set[str] = set()

    # If there's a pending (unresolved) proposal, use it as the base so chained
    # edits accumulate correctly instead of being rebased onto the saved version.
    pending = pending_proposal(conversation, "propose_pipeline_version")

    if pending and pending.tool_output:
        for f in pending.tool_output.get("files", []):
            current_files[f["name"]] = f["content"]
        deleted_paths.update(pending.tool_output.get("deleted_paths", []))
        all_paths.update(pending.tool_output.get("all_paths", []))
    else:
        current_version = pipeline.last_version if pipeline is not None else None
        if current_version and current_version.zipfile:
            with zipfile.ZipFile(io.BytesIO(bytes(current_version.zipfile)), "r") as zf:
                for name in zf.namelist():
                    if name.endswith("/"):
                        continue
                    all_paths.add(name)
                    try:
                        current_files[name] = zf.read(name).decode("utf-8")
                    except UnicodeDecodeError:
                        pass

    for f in modified_files or []:
        current_files[f.name] = f.content
        deleted_paths.discard(f.name)
        all_paths.add(f.name)

    if deleted_files:
        deletable_paths = all_paths | set(current_files) | deleted_paths
        resolved, unmatched = resolve_deleted_paths(deleted_files, deletable_paths)
        if unmatched:
            return nothing_to_delete_error(unmatched)
        deleted_paths |= resolved
        for name in resolved:
            current_files.pop(name, None)

    output = {
        "files": [{"name": k, "content": v} for k, v in current_files.items()],
        "deleted_paths": sorted(deleted_paths),
        "all_paths": sorted(all_paths),
    }
    message = resolve_commit_message(
        commit_message, pending.tool_output if pending else None
    )
    if message:
        output["commit_message"] = message
    return output
