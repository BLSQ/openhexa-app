import json

from pydantic import BaseModel

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.agents.proposals import (
    nothing_to_delete_error,
    resolve_deleted_paths,
)
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, ToolInvocation
from hexa.git.enums import FileEncoding
from hexa.mcp.tools.connections import list_connections
from hexa.mcp.tools.datasets import get_dataset, list_datasets, preview_dataset_file
from hexa.mcp.tools.files import list_files, read_file
from hexa.mcp.tools.help import get_help_or_doc
from hexa.mcp.tools.pipelines import get_pipeline, list_pipelines
from hexa.mcp.tools.webapps import get_static_webapp_file
from hexa.mcp.tools.workspaces import get_workspace
from hexa.webapps.models import GitWebapp

_MAX_INLINE_LINES = 300
_WEBAPP_ENTRY_POINT = "index.html"


class ProposedFile(BaseModel):
    path: str
    content: str


class FilePatch(BaseModel):
    path: str
    old_string: str
    new_string: str


def propose_webapp_version(
    webapp: GitWebapp,
    modified_files: list[ProposedFile] | None = None,
    file_patches: list[FilePatch] | str | None = None,
    deleted_files: list[str] | None = None,
    conversation: Conversation | None = None,
) -> dict:
    """Propose changes to the web app files.

    Two ways to describe changes — use whichever fits:

    - modified_files: pass the full new content for files you created or rewrote entirely
      (each entry needs a 'path' and 'content').
    - file_patches: for targeted edits to existing files, pass {path, old_string, new_string}.
      The backend finds old_string in the current file and replaces it with new_string.
      Prefer this over modified_files when changing a few lines of a large file — you
      only need to read and reproduce the lines that actually change.

    List any files to remove in deleted_files. A directory path removes everything under it.
    Deletions cover binary files (images, fonts) too, even though their content is never
    inlined here.
    Unchanged files are preserved automatically.
    You can mix modified_files and file_patches in the same call.
    """
    if isinstance(file_patches, str):
        try:
            raw = json.loads(file_patches)
            file_patches = [FilePatch(**item) for item in raw]
        except (json.JSONDecodeError, TypeError, ValueError):
            return {
                "error": "file_patches must be a list of {path, old_string, new_string} objects."
            }

    if not modified_files and not file_patches and not deleted_files:
        return {
            "error": (
                "No changes provided. Pass modified files in modified_files, "
                "targeted find/replace edits in file_patches, or paths to remove "
                "in deleted_files. Do not call this tool until you have the actual changes ready."
            )
        }

    current_files: dict[str, str] = {}
    deleted_paths: set[str] = set()

    pending = None
    if conversation is not None:
        pending = (
            ToolInvocation.objects.filter(
                message__conversation=conversation,
                tool_name="propose_webapp_version",
                success=True,
                proposal_pending=True,
            )
            .order_by("-created_at")
            .first()
        )

    repo_files = None
    if pending and pending.tool_output:
        for f in pending.tool_output.get("files", []):
            current_files[f["path"]] = f["content"]
        deleted_paths.update(pending.tool_output.get("deleted_paths", []))
    else:
        repo_files = webapp.get_files(include_binary_content=False)
        for f in repo_files:
            if f.get("encoding") == FileEncoding.TEXT and f.get("content") is not None:
                current_files[f["path"]] = f["content"]

    for patch in file_patches or []:
        if patch.path not in current_files:
            return {
                "error": f"Cannot patch '{patch.path}': file not found in the current version."
            }
        original = current_files[patch.path]
        if patch.old_string not in original:
            return {
                "error": (
                    f"Cannot patch '{patch.path}': old_string not found in the file. "
                    "Make sure it matches the current content exactly, including whitespace."
                )
            }
        current_files[patch.path] = original.replace(
            patch.old_string, patch.new_string, 1
        )

    for f in modified_files or []:
        current_files[f.path] = f.content
        deleted_paths.discard(f.path)

    if deleted_files:
        if repo_files is None:
            repo_files = webapp.get_files(include_binary_content=False)
        known_paths = (
            {f["path"] for f in repo_files if f.get("type") == "file"}
            | set(current_files)
            | deleted_paths
        )
        resolved, unmatched = resolve_deleted_paths(deleted_files, known_paths)
        if unmatched:
            return nothing_to_delete_error(unmatched)
        deleted_paths |= resolved
        for path in resolved:
            current_files.pop(path, None)

    return {
        "files": [{"path": k, "content": v} for k, v in current_files.items()],
        "deleted_paths": sorted(deleted_paths),
    }


class EditWebappAgent(BaseAgent):
    instruction_set = InstructionSet.EDIT_WEBAPP
    history_strip_tools = {"propose_webapp_version"}
    tools = [
        get_workspace,
        get_help_or_doc,
        get_static_webapp_file,
        list_datasets,
        get_dataset,
        preview_dataset_file,
        list_connections,
        list_files,
        read_file,
        list_pipelines,
        get_pipeline,
        propose_webapp_version,
    ]

    @property
    def _context(self) -> dict:
        ctx = super()._context
        return {
            **ctx,
            "webapp": self.conversation.linked_object,
            "conversation": self.conversation,
        }

    async def _on_tool_result(self, invocation: ToolInvocation) -> None:
        if invocation.tool_name != "propose_webapp_version" or not invocation.success:
            return
        # Supersede any earlier pending proposal so only the latest one awaits user
        # action. The flag is load-bearing: proposal outputs are stripped from the
        # history sent to the model, so the pending invocation is the only source
        # for re-inlining the proposed files in instructions and for chaining.
        await ToolInvocation.objects.filter(
            message__conversation=self.conversation,
            tool_name="propose_webapp_version",
            proposal_pending=True,
        ).aupdate(proposal_pending=False)
        invocation.proposal_pending = True

    def _extra_instructions(self) -> str:
        linked_object = self.conversation.linked_object
        if linked_object is None:
            return ""
        if not isinstance(linked_object, GitWebapp):
            raise TypeError(
                f"EditWebappAgent requires a GitWebapp linked object, got {type(linked_object).__name__}"
            )
        webapp = linked_object

        lines = [
            "## Current Web App",
            f"Name: {webapp.name}",
            f"Slug: {webapp.slug}",
            f"Workspace: {webapp.workspace.slug}",
        ]
        if webapp.description:
            lines.append(f"Description: {webapp.description}")

        pending = (
            ToolInvocation.objects.filter(
                message__conversation=self.conversation,
                tool_name="propose_webapp_version",
                success=True,
                proposal_pending=True,
            )
            .order_by("-created_at")
            .first()
        )

        if pending and pending.tool_output:
            proposed_files = pending.tool_output.get("files", [])
            pending_deletions = pending.tool_output.get("deleted_paths", [])
            if pending_deletions:
                lines.append("")
                lines.append(
                    "### Files Staged For Deletion (Pending)\n"
                    "The pending proposal drops these. The user can still restore any of "
                    "them in the editor without the proposal being resolved, so this is "
                    "the proposal's state, not their final intent: if they ask for one "
                    "back, re-add it with `modified_files` rather than telling them it is "
                    "gone. Re-listing an already-staged path in `deleted_files` is harmless."
                )
                for path in pending_deletions:
                    lines.append(f"- `{path}`")
            if proposed_files:
                lines.append("")
                lines.append(
                    "### Files (Pending Proposed Version — not yet accepted by the user)\n"
                    "Use these files as the base for any further changes."
                )
                for f in proposed_files:
                    content = f["content"]
                    line_count = content.count("\n") + 1
                    if line_count > _MAX_INLINE_LINES:
                        lines.append(
                            f"\n#### {f['path']} ({line_count} lines — not shown)\n"
                            f"This file is part of the pending version. "
                            f"Omit it from `modified_files` to preserve it unchanged."
                        )
                    else:
                        lines.append(f"\n#### {f['path']}\n```\n{content}\n```")
        else:
            all_files = webapp.get_files()
            lines.append("")
            lines.append(
                "### Files\n"
                f"Call `get_static_webapp_file` with webapp slug `{webapp.slug}` "
                f"and the file path to read any text file. "
                f"For large files pass `start_line` and `end_line` to read only the relevant section."
            )
            for f in all_files:
                if f.get("encoding") == FileEncoding.TEXT:
                    line_count = f.get("line_count") or 0
                    if (
                        f["path"] == _WEBAPP_ENTRY_POINT
                        and line_count <= _MAX_INLINE_LINES
                        and f.get("content") is not None
                    ):
                        lines.append(f"\n#### {f['path']}\n```\n{f['content']}\n```")
                    else:
                        line_info = f" ({line_count} lines)" if line_count else ""
                        lines.append(f"- `{f['path']}`{line_info}")
                else:
                    lines.append(f"- `{f['path']}` (binary)")

        return "\n".join(lines)
