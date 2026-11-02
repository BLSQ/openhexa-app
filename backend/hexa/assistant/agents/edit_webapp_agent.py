from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.keys import AgentKey
from hexa.git.enums import FileEncoding
from hexa.mcp.tools.connections import list_connections
from hexa.mcp.tools.databases import get_db_schema, get_db_table_schema
from hexa.mcp.tools.datasets import get_dataset, list_datasets, preview_dataset_file
from hexa.mcp.tools.files import list_files, read_file
from hexa.mcp.tools.help import get_help_or_doc
from hexa.mcp.tools.pipelines import get_pipeline, list_pipelines
from hexa.mcp.tools.saved_queries import (
    create_saved_query,
    get_saved_query,
    list_saved_queries,
    update_saved_query,
)
from hexa.mcp.tools.webapps import (
    edit_static_webapp_file,
    get_static_webapp_file,
    update_static_webapp,
)
from hexa.webapps.models import GitWebapp

_MAX_INLINE_LINES = 300
_WEBAPP_ENTRY_POINT = "index.html"


class EditWebappAgent(BaseAgent):
    """Edits a static web app by committing directly with the MCP write tools.

    Every successful tool call is a new version on main that the user sees in the
    editor and preview right away; publishing stays a manual step in the UI.
    """

    instruction_set = InstructionSet.EDIT_WEBAPP
    agent_key = AgentKey.EDIT_WEBAPP
    tools = [
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
        get_db_schema,
        get_db_table_schema,
        list_saved_queries,
        get_saved_query,
        create_saved_query,
        update_saved_query,
        update_static_webapp,
        edit_static_webapp_file,
    ]

    @property
    def _context(self) -> dict:
        ctx = super()._context
        webapp = self.conversation.linked_object
        if webapp is None:
            return ctx
        return {**ctx, "webapp_id": str(webapp.id)}

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

        all_files = webapp.get_files()
        lines.append("")
        lines.append(
            "### Files (latest version)\n"
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
