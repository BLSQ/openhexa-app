from asgiref.sync import sync_to_async
from django.contrib.contenttypes.models import ContentType

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.keys import AgentKey
from hexa.mcp.tools.connections import list_connections
from hexa.mcp.tools.databases import get_db_schema, get_db_table_schema
from hexa.mcp.tools.datasets import get_dataset, list_datasets, preview_dataset_file
from hexa.mcp.tools.files import list_files, read_file
from hexa.mcp.tools.help import get_help_or_doc
from hexa.mcp.tools.saved_queries import (
    create_saved_query,
    get_saved_query,
    list_saved_queries,
)
from hexa.mcp.tools.webapps import create_static_webapp
from hexa.webapps.models import GitWebapp


class CreateWebappAgent(BaseAgent):
    instruction_set = InstructionSet.CREATE_WEBAPPS
    agent_key = AgentKey.CREATE_WEBAPP
    tools = [
        get_help_or_doc,
        list_datasets,
        get_dataset,
        preview_dataset_file,
        list_connections,
        list_files,
        read_file,
        get_db_schema,
        get_db_table_schema,
        list_saved_queries,
        get_saved_query,
        create_saved_query,
        create_static_webapp,
    ]

    async def _on_tool_result(self, invocation) -> None:
        if invocation.tool_name != "create_static_webapp" or not invocation.success:
            return
        webapp_id = ((invocation.tool_output or {}).get("webapp") or {}).get("id")
        if not webapp_id:
            return
        webapp = await GitWebapp.objects.aget(id=webapp_id)
        # The conversation follows the user to the code editor, where it continues as an edit.
        ct = await sync_to_async(ContentType.objects.get_for_model)(GitWebapp)
        self.conversation.linked_object_content_type = ct
        self.conversation.linked_object_id = webapp.id
        self.conversation.instruction_set = InstructionSet.EDIT_WEBAPP
        await self.conversation.asave()
