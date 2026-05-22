import io
import zipfile

from pydantic import BaseModel

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, ToolInvocation
from hexa.mcp.tools.connections import list_connections
from hexa.mcp.tools.datasets import get_dataset, list_datasets, preview_dataset_file
from hexa.mcp.tools.files import list_files, read_file
from hexa.mcp.tools.help import get_help_or_doc
from hexa.pipelines.models import Pipeline


class ProposedFile(BaseModel):
    name: str
    content: str


def propose_pipeline_version(
    pipeline: Pipeline,
    modified_files: list[ProposedFile] | None = None,
    deleted_files: list[str] | None = None,
    conversation: Conversation | None = None,
) -> dict:
    """Propose a new version of the pipeline.

    Always call this tool with the files you modified or created in modified_files.
    Each entry must have a 'name' (e.g. 'pipeline.py') and 'content' (the full file text).
    List any files to remove in deleted_files.
    Unchanged files are preserved automatically.
    """
    current_files: dict[str, str] = {}

    # If there's a pending (unresolved) proposal, use it as the base so chained
    # edits accumulate correctly instead of being rebased onto the saved version.
    pending = None
    if conversation is not None:
        pending = (
            ToolInvocation.objects.filter(
                message__conversation=conversation,
                tool_name="propose_pipeline_version",
                success=True,
                resolved=False,
            )
            .order_by("-created_at")
            .first()
        )

    if pending and pending.tool_output:
        for f in pending.tool_output.get("files", []):
            current_files[f["name"]] = f["content"]
    else:
        current_version = pipeline.last_version if pipeline is not None else None
        if current_version and current_version.zipfile:
            with zipfile.ZipFile(io.BytesIO(bytes(current_version.zipfile)), "r") as zf:
                for name in zf.namelist():
                    if name.endswith("/"):
                        continue
                    try:
                        current_files[name] = zf.read(name).decode("utf-8")
                    except UnicodeDecodeError:
                        pass

    for f in modified_files or []:
        current_files[f.name] = f.content
    for name in deleted_files or []:
        if name.endswith("/"):
            for key in list(current_files.keys()):
                if key.startswith(name):
                    current_files.pop(key)
        else:
            current_files.pop(name, None)

    return {"files": [{"name": k, "content": v} for k, v in current_files.items()]}


class EditPipelineAgent(BaseAgent):
    instruction_set = InstructionSet.EDIT_PIPELINE
    tools = [
        get_help_or_doc,
        list_datasets,
        get_dataset,
        preview_dataset_file,
        list_connections,
        list_files,
        read_file,
        propose_pipeline_version,
    ]

    @property
    def _context(self) -> dict:
        ctx = super()._context
        return {
            **ctx,
            "pipeline": self.conversation.linked_object,
            "conversation": self.conversation,
        }

    def _extra_instructions(self) -> str:
        linked_object = self.conversation.linked_object
        if linked_object is None:
            return ""
        if not isinstance(linked_object, Pipeline):
            raise TypeError(
                f"EditPipelineAgent requires a Pipeline linked object, got {type(linked_object).__name__}"
            )
        pipeline = linked_object

        lines = [
            "## Current Pipeline",
            f"Name: {pipeline.name}",
            f"Code: {pipeline.code}",
        ]
        if pipeline.description:
            lines.append(f"Description: {pipeline.description}")

        current_version = pipeline.last_version
        if not current_version:
            return "\n".join(lines)

        lines.append(f"Current version: {current_version.version_name}")

        pending = (
            ToolInvocation.objects.filter(
                message__conversation=self.conversation,
                tool_name="propose_pipeline_version",
                success=True,
                resolved=False,
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
                    lines.append(f"\n#### {f['name']}\n```\n{f['content']}\n```")
        elif current_version.zipfile:
            lines.append("")
            lines.append("### Files")
            with zipfile.ZipFile(io.BytesIO(bytes(current_version.zipfile)), "r") as zf:
                for name in sorted(zf.namelist()):
                    if name.endswith("/"):
                        continue
                    try:
                        content = zf.read(name).decode("utf-8")
                    except UnicodeDecodeError:
                        continue
                    lines.append(f"\n#### {name}\n```\n{content}\n```")

        return "\n".join(lines)
