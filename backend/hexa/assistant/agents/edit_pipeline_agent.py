import io
import zipfile

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.keys import AgentKey
from hexa.assistant.models import ToolInvocation
from hexa.assistant.tools.pipelines import propose_pipeline_version
from hexa.assistant.tools.proposals import pending_proposal
from hexa.mcp.tools.connections import list_connections
from hexa.mcp.tools.datasets import get_dataset, list_datasets, preview_dataset_file
from hexa.mcp.tools.files import glob_files, grep_files, list_files, read_file
from hexa.mcp.tools.help import get_help_or_doc
from hexa.pipelines.models import Pipeline


class EditPipelineAgent(BaseAgent):
    instruction_set = InstructionSet.EDIT_PIPELINE
    agent_key = AgentKey.EDIT_PIPELINE
    tools = [
        get_help_or_doc,
        list_datasets,
        get_dataset,
        preview_dataset_file,
        list_connections,
        list_files,
        glob_files,
        grep_files,
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

    async def _on_tool_result(self, invocation: ToolInvocation) -> None:
        if invocation.tool_name != "propose_pipeline_version" or not invocation.success:
            return
        # Supersede any earlier pending proposal in this conversation so only the
        # latest one awaits user action, then mark this invocation as pending so it
        # re-surfaces in the UI on page reload (the agent itself sees the proposed
        # files via the replayed message history regardless of this flag).
        await ToolInvocation.objects.filter(
            message__conversation=self.conversation,
            tool_name="propose_pipeline_version",
            proposal_pending=True,
        ).aupdate(proposal_pending=False)
        invocation.proposal_pending = True

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

        pending = pending_proposal(self.conversation, "propose_pipeline_version")

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
                        # Listed without content so the agent can still delete it by path.
                        lines.append(f"- `{name}` (binary)")
                        continue
                    lines.append(f"\n#### {name}\n```\n{content}\n```")

        return "\n".join(lines)
