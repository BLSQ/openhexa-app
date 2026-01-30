import json
import logging

from anthropic import Anthropic
from django.conf import settings
from django.db.models import F

from hexa.workspaces.models import Workspace

from .models import (
    ASSISTANT_MODELS,
    DEFAULT_ASSISTANT_MODEL,
    Conversation,
    Message,
    PendingToolApproval,
    ToolExecution,
)
from .tool_executors import WorkspaceDatabaseTools, WorkspaceFileSystemTools
from .tools import get_tools_for_api, get_tools_requiring_approval

logger = logging.getLogger(__name__)

MAX_TOOL_ITERATIONS = 10

SYSTEM_PROMPT = """You are a helpful AI assistant integrated into OpenHEXA, a data platform. You have access to the user's workspace file system and PostgreSQL database.

You can:
- List, read, write, and search files in the workspace file system
- Query the workspace database with SELECT statements
- Explore database schemas and table structures

Guidelines:
- When querying databases, start by exploring the schema if you're unsure about table structures
- Present query results in a clear, readable format
- If a query fails, suggest corrections
- Be professional and concise in your responses
"""


class AgentService:
    def __init__(self, workspace: Workspace, conversation: Conversation):
        self.workspace = workspace
        self.conversation = conversation
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.fs_tools = WorkspaceFileSystemTools(workspace)
        self.db_tools = WorkspaceDatabaseTools(workspace)

        org = workspace.organization
        org_model = getattr(org, "assistant_model", "") if org else ""
        self.model_id = (
            org_model
            if org_model and org_model in ASSISTANT_MODELS
            else DEFAULT_ASSISTANT_MODEL
        )
        model_config = ASSISTANT_MODELS[self.model_id]
        self.input_price_per_million = model_config["input_price_per_million"]
        self.output_price_per_million = model_config["output_price_per_million"]

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

    def _serialize_response(self, response) -> dict:
        content = []
        for block in response.content:
            if block.type == "text":
                content.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                content.append(
                    {
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    }
                )
        return {
            "content": content,
            "stop_reason": response.stop_reason,
        }

    def _deserialize_response_content(self, serialized: dict) -> list:
        return serialized["content"]

    def _serialize_messages(self, messages: list) -> list:
        serialized = []
        for msg in messages:
            if msg["role"] == "assistant" and not isinstance(msg["content"], str):
                content = []
                for block in msg["content"]:
                    if hasattr(block, "type"):
                        if block.type == "text":
                            content.append({"type": "text", "text": block.text})
                        elif block.type == "tool_use":
                            content.append(
                                {
                                    "type": "tool_use",
                                    "id": block.id,
                                    "name": block.name,
                                    "input": block.input,
                                }
                            )
                    else:
                        content.append(block)
                serialized.append({"role": msg["role"], "content": content})
            else:
                serialized.append(msg)
        return serialized

    def send_message(self, user_message: str) -> dict:
        messages = []
        for msg in self.conversation.messages.all():
            messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": user_message})

        return self._process_with_tools(messages, user_message)

    def resume_after_approval(self, pending_approval: PendingToolApproval) -> dict:
        messages = pending_approval.messages_snapshot
        claude_response_content = self._deserialize_response_content(
            pending_approval.claude_response
        )

        tool_use = None
        for block in claude_response_content:
            if (
                block.get("type") == "tool_use"
                and block.get("id") == pending_approval.tool_use_id
            ):
                tool_use = block
                break

        if not tool_use:
            return {"error": "Tool use not found in saved response"}

        result = self.execute_tool(tool_use["name"], tool_use["input"])

        tool_results = [
            {
                "type": "tool_result",
                "tool_use_id": tool_use["id"],
                "content": json.dumps(result),
            }
        ]

        messages.append({"role": "assistant", "content": claude_response_content})
        messages.append({"role": "user", "content": tool_results})

        tools = get_tools_for_api()

        response = self.client.messages.create(
            model=self.model_id,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )

        total_input_tokens = (
            pending_approval.input_tokens_so_far + response.usage.input_tokens
        )
        total_output_tokens = (
            pending_approval.output_tokens_so_far + response.usage.output_tokens
        )

        return self._continue_tool_loop(
            messages,
            response,
            total_input_tokens,
            total_output_tokens,
        )

    def _process_with_tools(self, messages: list, user_message: str) -> dict:
        tools = get_tools_for_api()

        if not self.conversation.model:
            Conversation.objects.filter(id=self.conversation.id).update(
                model=self.model_id
            )

        Message.objects.create(
            conversation=self.conversation,
            role="user",
            content=user_message,
        )

        response = self.client.messages.create(
            model=self.model_id,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )

        total_input_tokens = response.usage.input_tokens
        total_output_tokens = response.usage.output_tokens

        return self._continue_tool_loop(
            messages,
            response,
            total_input_tokens,
            total_output_tokens,
        )

    def _continue_tool_loop(
        self,
        messages: list,
        response,
        total_input_tokens: int,
        total_output_tokens: int,
    ) -> dict:
        tools = get_tools_for_api()
        tools_requiring_approval = get_tools_requiring_approval()

        iterations = 0
        while response.stop_reason == "tool_use" and iterations < MAX_TOOL_ITERATIONS:
            iterations += 1
            tool_uses = [
                block for block in response.content if block.type == "tool_use"
            ]

            tools_needing_approval = [
                tu for tu in tool_uses if tu.name in tools_requiring_approval
            ]

            if tools_needing_approval:
                tool_use = tools_needing_approval[0]
                return self._create_pending_approval(
                    tool_use,
                    messages,
                    response,
                    total_input_tokens,
                    total_output_tokens,
                )

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
                model=self.model_id,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=messages,
            )

            total_input_tokens += response.usage.input_tokens
            total_output_tokens += response.usage.output_tokens

        return self._finalize_response(
            response, total_input_tokens, total_output_tokens
        )

    def _create_pending_approval(
        self,
        tool_use,
        messages: list,
        response,
        input_tokens: int,
        output_tokens: int,
    ) -> dict:
        pending = PendingToolApproval.objects.create(
            conversation=self.conversation,
            tool_use_id=tool_use.id,
            tool_name=tool_use.name,
            tool_input=tool_use.input,
            claude_response=self._serialize_response(response),
            messages_snapshot=self._serialize_messages(messages),
            input_tokens_so_far=input_tokens,
            output_tokens_so_far=output_tokens,
        )

        return {
            "status": "awaiting_approval",
            "pending_tool": {
                "id": str(pending.id),
                "tool_name": tool_use.name,
                "tool_input": tool_use.input,
                "created_at": pending.created_at,
            },
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": 0,
            },
        }

    def _finalize_response(
        self,
        response,
        total_input_tokens: int,
        total_output_tokens: int,
    ) -> dict:
        final_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                final_text += block.text

        cost = (total_input_tokens / 1_000_000) * self.input_price_per_million + (
            total_output_tokens / 1_000_000
        ) * self.output_price_per_million

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
            "status": "complete",
            "response": final_text,
            "usage": {
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "cost": float(cost),
            },
        }
