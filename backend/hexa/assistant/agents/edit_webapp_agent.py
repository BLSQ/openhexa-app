from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.keys import AgentKey
from hexa.assistant.models import ToolInvocation
from hexa.assistant.tools.proposals import pending_proposal
from hexa.assistant.tools.webapps import (
    glob_webapp_files,
    grep_webapp_files,
    propose_webapp_version,
    read_webapp_file,
)
from hexa.git.enums import FileEncoding
from hexa.mcp.tools.connections import list_connections
from hexa.mcp.tools.databases import get_db_schema, get_db_table_schema
from hexa.mcp.tools.datasets import get_dataset, list_datasets, preview_dataset_file
from hexa.mcp.tools.files import glob_files, grep_files, list_files, read_file
from hexa.mcp.tools.help import get_help_or_doc
from hexa.mcp.tools.pipelines import get_pipeline, list_pipelines
from hexa.mcp.tools.saved_queries import (
    create_saved_query,
    get_saved_query,
    list_saved_queries,
    update_saved_query,
)
from hexa.webapps.models import GitWebapp

_MAX_INLINE_LINES = 300
_WEBAPP_ENTRY_POINT = "index.html"


class EditWebappAgent(BaseAgent):
    instruction_set = InstructionSet.EDIT_WEBAPP
    agent_key = AgentKey.EDIT_WEBAPP
    history_strip_tools = {"propose_webapp_version"}
    tools = [
        get_help_or_doc,
        glob_webapp_files,
        grep_webapp_files,
        read_webapp_file,
        list_datasets,
        get_dataset,
        preview_dataset_file,
        list_connections,
        list_files,
        glob_files,
        grep_files,
        read_file,
        list_pipelines,
        get_pipeline,
        get_db_schema,
        get_db_table_schema,
        list_saved_queries,
        get_saved_query,
        create_saved_query,
        update_saved_query,
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

        pending = pending_proposal(self.conversation, "propose_webapp_version")

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
                "Call `read_webapp_file` with a file path to read any text file. "
                "Locate code with `grep_webapp_files` first and read only that section."
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
