import json
import logging

from anthropic import Anthropic
from django.conf import settings
from django.db.models import F

from hexa.workspaces.models import Workspace

from .models import Conversation, Message, ToolExecution
from .tool_executors import WorkspaceDatabaseTools, WorkspaceFileSystemTools
from .tools import get_database_tools, get_file_system_tools

logger = logging.getLogger(__name__)

INPUT_PRICE_PER_MILLION = 5.00
OUTPUT_PRICE_PER_MILLION = 25.00
MAX_TOOL_ITERATIONS = 10

SYSTEM_PROMPT = """You are a helpful AI assistant integrated into OpenHEXA, a data platform. You have access to the user's workspace file system and PostgreSQL database.

You can:
- List, read, write, and search files in the workspace file system
- Query the workspace database with SELECT statements
- Explore database schemas and table structures

Guidelines:
- Explain what you're doing when using tools
- Ask for confirmation before writing files
- When querying databases, start by exploring the schema if you're unsure about table structures
- Present query results in a clear, readable format
- If a query fails, suggest corrections
"""


class AgentService:
    def __init__(self, workspace: Workspace, conversation: Conversation):
        self.workspace = workspace
        self.conversation = conversation
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.fs_tools = WorkspaceFileSystemTools(workspace)
        self.db_tools = WorkspaceDatabaseTools(workspace)

    def execute_tool(self, tool_name: str, tool_input: dict) -> dict:
        if tool_name == "list_files":
            result = self.fs_tools.list_files(tool_input.get("path", ""))
        elif tool_name == "read_file":
            result = self.fs_tools.read_file(tool_input["path"])
        elif tool_name == "write_file":
            result = self.fs_tools.write_file(tool_input["path"], tool_input["content"])
        elif tool_name == "search_files":
            result = self.fs_tools.search_files(
                tool_input["pattern"], tool_input.get("path", "")
            )
        elif tool_name == "query_database":
            result = self.db_tools.query_database(
                tool_input["query"], tool_input.get("limit", 100)
            )
        elif tool_name == "describe_tables":
            result = self.db_tools.describe_tables(tool_input.get("table_name"))
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        ToolExecution.objects.create(
            conversation=self.conversation,
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=result,
            success="error" not in result,
        )

        return result

    def send_message(self, user_message: str) -> dict:
        messages = []
        for msg in self.conversation.messages.all():
            messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": user_message})

        tools = get_file_system_tools() + get_database_tools()

        response = self.client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )

        total_input_tokens = response.usage.input_tokens
        total_output_tokens = response.usage.output_tokens

        iterations = 0
        while response.stop_reason == "tool_use" and iterations < MAX_TOOL_ITERATIONS:
            iterations += 1
            tool_uses = [block for block in response.content if block.type == "tool_use"]

            tool_results = []
            for tool_use in tool_uses:
                result = self.execute_tool(tool_use.name, tool_use.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": json.dumps(result),
                    }
                )

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

            response = self.client.messages.create(
                model="claude-opus-4-5-20251101",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=messages,
            )

            total_input_tokens += response.usage.input_tokens
            total_output_tokens += response.usage.output_tokens

        final_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                final_text += block.text

        cost = (total_input_tokens / 1_000_000) * INPUT_PRICE_PER_MILLION + (
            total_output_tokens / 1_000_000
        ) * OUTPUT_PRICE_PER_MILLION

        Message.objects.create(
            conversation=self.conversation,
            role="user",
            content=user_message,
        )

        Message.objects.create(
            conversation=self.conversation,
            role="assistant",
            content=final_text,
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens,
            cost=cost,
        )

        Conversation.objects.filter(id=self.conversation.id).update(
            total_input_tokens=F("total_input_tokens") + total_input_tokens,
            total_output_tokens=F("total_output_tokens") + total_output_tokens,
            estimated_cost=F("estimated_cost") + cost,
        )

        return {
            "response": final_text,
            "usage": {
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "cost": float(cost),
            },
        }
