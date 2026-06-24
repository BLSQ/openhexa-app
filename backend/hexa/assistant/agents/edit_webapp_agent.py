from pydantic import BaseModel

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, ToolInvocation
from hexa.git.enums import FileEncoding
from hexa.mcp.tools.connections import list_connections
from hexa.mcp.tools.datasets import get_dataset, list_datasets, preview_dataset_file
from hexa.mcp.tools.files import list_files, read_file
from hexa.mcp.tools.help import get_help_or_doc
from hexa.mcp.tools.webapps import get_static_webapp_file
from hexa.webapps.models import GitWebapp

_MAX_INLINE_LINES = 300


class ProposedFile(BaseModel):
    path: str
    content: str


def propose_webapp_version(
    webapp: GitWebapp,
    modified_files: list[ProposedFile] | None = None,
    deleted_files: list[str] | None = None,
    conversation: Conversation | None = None,
) -> dict:
    """Propose changes to the web app files.

    Pass the files you modified or created in modified_files (each with a 'path' and 'content').
    List any files to remove in deleted_files.
    Unchanged files are preserved automatically.
    """
    current_files: dict[str, str] = {}

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

    if pending and pending.tool_output:
        for f in pending.tool_output.get("files", []):
            current_files[f["path"]] = f["content"]
    else:
        for f in webapp.get_files():
            if f.get("encoding") == FileEncoding.TEXT and f.get("content") is not None:
                current_files[f["path"]] = f["content"]

    for f in modified_files or []:
        current_files[f.path] = f.content
    for path in deleted_files or []:
        current_files.pop(path, None)

    return {"files": [{"path": k, "content": v} for k, v in current_files.items()]}


class EditWebappAgent(BaseAgent):
    instruction_set = InstructionSet.EDIT_WEBAPP
    tools = [
        get_help_or_doc,
        get_static_webapp_file,
        list_datasets,
        get_dataset,
        preview_dataset_file,
        list_connections,
        list_files,
        read_file,
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
                f"and the file path to read any text file."
            )
            for f in all_files:
                if f.get("encoding") == FileEncoding.TEXT:
                    line_info = (
                        f" ({f['line_count']} lines)" if f.get("line_count") else ""
                    )
                    lines.append(f"- `{f['path']}`{line_info}")
                else:
                    lines.append(f"- `{f['path']}` (binary)")

        return "\n".join(lines)
