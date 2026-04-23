import json
import logging
from decimal import Decimal

import genai_prices
from asgiref.sync import async_to_sync
from pydantic_ai import Agent, RunUsage
from pydantic_ai.messages import (
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    ModelMessagesTypeAdapter,
    ModelResponse,
    PartDeltaEvent,
    PartStartEvent,
    TextPart,
    TextPartDelta,
    ToolReturnPart,
)

from hexa.assistant.instructions import InstructionSet, get_instructions
from hexa.assistant.model_builder import AiModelBuilder
from hexa.assistant.models import Conversation, Message, ToolInvocation
from hexa.assistant.tool_binding import bind_context
from hexa.core.sse import format_sse

logger = logging.getLogger(__name__)


def _is_success(content) -> bool:
    if isinstance(content, str):
        try:
            data = json.loads(content)
        except ValueError:
            return False
    else:
        data = content
    if not isinstance(data, dict):
        return True
    if data.get("errors"):
        return False
    for value in data.values():
        if isinstance(value, dict) and value.get("errors"):
            return False
    return True


_NAMING_INSTRUCTIONS = (
    "Generate a short title (max 5 words) for a conversation based on the user's first message. "
    "Reply with only the title, no punctuation, no quotes."
)


class BaseAgent:
    instruction_set = InstructionSet.GENERAL
    tools: list = []

    def __init__(self, conversation: Conversation):
        self.conversation = conversation
        builder = AiModelBuilder.from_conversation(conversation)
        self._model_api_name = builder.model_api_name
        self._provider_id = builder.provider_id
        self._model = builder.build()

        instructions = get_instructions(self.instruction_set)
        extra = self._extra_instructions()
        if extra:
            instructions += "\n\n" + extra

        self.agent = Agent(
            model=self._model,
            instructions=instructions,
            tools=self._tools_with_context,
            end_strategy="exhaustive",
        )

    def _extra_instructions(self) -> str:
        return ""

    @property
    def _tools_with_context(self) -> list:
        return [bind_context(func, self._context) for func in self.tools]

    @property
    def _context(self) -> dict:
        return {
            "user": self.conversation.user,
            "workspace_slug": self.conversation.workspace.slug,
        }

    def run(self, user_input: str) -> None:
        async def _consume():
            async for _ in self.run_stream(user_input):
                pass

        async_to_sync(_consume)()

    async def run_stream(self, user_input: str):
        is_first_message = self.conversation.name is None

        user_msg = await Message.objects.acreate(
            conversation=self.conversation,
            role=Message.Role.USER,
            content=user_input,
        )
        yield format_sse(
            "user_message", {"id": str(user_msg.id), "content": user_input}
        )

        history = ModelMessagesTypeAdapter.validate_python(
            self.conversation.messages_history
        )
        logger.info(
            "agent.run_stream: conversation=%s history_len=%d",
            self.conversation.id,
            len(history),
        )

        try:
            tool_invocations: dict[str, ToolInvocation] = {}

            async with self.agent.iter(
                user_input, message_history=history
            ) as agent_run:
                async for node in agent_run:
                    if self.agent.is_model_request_node(node):
                        async for sse in self._stream_model_node(node, agent_run.ctx):
                            yield sse
                    elif self.agent.is_call_tools_node(node):
                        async for sse in self._stream_tools_node(
                            node, agent_run.ctx, tool_invocations
                        ):
                            yield sse
                run_result = agent_run.result

            response_text = self._extract_response_text(
                run_result.new_messages() if run_result else []
            )
            all_messages = run_result.all_messages() if run_result else []
            usage = run_result.usage() if run_result else RunUsage()

            assistant_message = await self._persist_run(
                response_text,
                tool_invocations,
                usage,
                all_messages,
                is_first_message,
                user_input,
            )
            yield format_sse(
                "done",
                {
                    "message_id": str(assistant_message.id),
                    "name": self.conversation.name,
                },
            )

        except Exception:
            logger.exception("agent.run_stream: error during streaming")
            yield format_sse("error", {"message": "An error occurred"})

    @staticmethod
    async def _stream_model_node(node, ctx):
        async with node.stream(ctx) as model_stream:
            async for event in model_stream:
                if isinstance(event, PartStartEvent) and isinstance(
                    event.part, TextPart
                ):
                    if event.part.content:
                        yield format_sse("text_delta", {"delta": event.part.content})
                elif isinstance(event, PartDeltaEvent) and isinstance(
                    event.delta, TextPartDelta
                ):
                    yield format_sse("text_delta", {"delta": event.delta.content_delta})

    @staticmethod
    async def _stream_tools_node(
        node, ctx, tool_invocations: dict[str, ToolInvocation]
    ):
        async with node.stream(ctx) as tools_stream:
            async for event in tools_stream:
                if isinstance(event, FunctionToolCallEvent):
                    call = event.part
                    logger.info(
                        "agent.run_stream: tool_call tool=%s call_id=%s",
                        call.tool_name,
                        call.tool_call_id,
                    )
                    raw_args = call.args
                    tool_input = (
                        json.loads(raw_args)
                        if isinstance(raw_args, str)
                        else json.loads(json.dumps(raw_args, default=str))
                    )
                    tool_invocations[call.tool_call_id] = ToolInvocation(
                        tool_call_id=call.tool_call_id,
                        tool_name=call.tool_name,
                        tool_input=tool_input,
                    )
                    yield format_sse(
                        "tool_call",
                        {
                            "tool_call_id": call.tool_call_id,
                            "tool_name": call.tool_name,
                        },
                    )
                elif isinstance(event, FunctionToolResultEvent):
                    if not isinstance(event.result, ToolReturnPart):
                        continue
                    result_part = event.result
                    logger.info(
                        "agent.run_stream: tool_result call_id=%s",
                        result_part.tool_call_id,
                    )
                    content = result_part.content
                    if isinstance(content, str):
                        try:
                            tool_output = json.loads(content)
                        except (json.JSONDecodeError, ValueError):
                            tool_output = content
                    else:
                        tool_output = json.loads(json.dumps(content, default=str))
                    success = _is_success(content)
                    if result_part.tool_call_id in tool_invocations:
                        inv = tool_invocations[result_part.tool_call_id]
                        inv.tool_output = tool_output
                        inv.success = success
                    else:
                        tool_invocations[result_part.tool_call_id] = ToolInvocation(
                            tool_call_id=result_part.tool_call_id,
                            tool_name=result_part.tool_name,
                            tool_input="",
                            tool_output=tool_output,
                            success=success,
                        )
                    yield format_sse(
                        "tool_result",
                        {
                            "tool_call_id": result_part.tool_call_id,
                            "tool_name": result_part.tool_name,
                            "success": success,
                            "tool_output": tool_output,
                        },
                    )

    @staticmethod
    def _extract_response_text(new_messages: list) -> str:
        texts = [
            part.content
            for msg in new_messages
            if isinstance(msg, ModelResponse)
            for part in msg.parts
            if isinstance(part, TextPart) and part.content
        ]
        return "\n\n".join(texts)

    async def _persist_run(
        self,
        response_text: str,
        tool_invocations: dict[str, ToolInvocation],
        usage: RunUsage,
        all_messages: list,
        is_first_message: bool,
        user_input: str,
    ) -> Message:
        input_tok = usage.input_tokens or 0
        output_tok = usage.output_tokens or 0
        cost = self._get_cost(usage)
        logger.info(
            "agent.run_stream: done input_tokens=%d output_tokens=%d cost=%s",
            input_tok,
            output_tok,
            cost,
        )

        assistant_message = await Message.objects.acreate(
            conversation=self.conversation,
            role=Message.Role.ASSISTANT,
            content=response_text,
            input_tokens=input_tok,
            output_tokens=output_tok,
            cost=cost,
        )
        for tool_invocation in tool_invocations.values():
            tool_invocation.message = assistant_message
            await tool_invocation.asave()

        self.conversation.total_input_tokens += input_tok
        self.conversation.total_output_tokens += output_tok
        if cost is not None:
            self.conversation.cost += cost
        self.conversation.messages_history = ModelMessagesTypeAdapter.dump_python(
            all_messages, mode="json"
        )

        update_fields = [
            "total_input_tokens",
            "total_output_tokens",
            "cost",
            "messages_history",
            "updated_at",
        ]
        if is_first_message:
            name, naming_usage = await self._generate_conversation_name(user_input)
            self.conversation.name = name
            naming_cost = self._get_cost(naming_usage)
            if naming_cost is not None:
                self.conversation.cost += naming_cost
            update_fields.append("name")

        await self.conversation.asave(update_fields=update_fields)
        return assistant_message

    async def _generate_conversation_name(
        self, user_input: str
    ) -> tuple[str, RunUsage]:
        # TODO: Execute in parallel with DB writes using asyncio.gather for performance
        # TODO: Use smaller, cheaper models for these small "utility agents"
        naming_agent = Agent(model=self._model, instructions=_NAMING_INSTRUCTIONS)
        try:
            result = await naming_agent.run(user_input)
            return result.output.strip()[:50], result.usage()
        except Exception:
            logger.warning(
                "agent.run: conversation naming failed, falling back to truncation"
            )
            text = " ".join(user_input.split())
            truncated = text[:50].rsplit(" ", 1)[0]
            return truncated or text[:50], RunUsage()

    def _get_cost(self, usage: RunUsage) -> Decimal | None:
        cost: Decimal | None = None
        try:
            price_calc = genai_prices.calc_price(
                usage, self._model_api_name, provider_id=self._provider_id
            )
            cost = price_calc.total_price
        except Exception:
            logger.warning(
                "agent.run: cost calculation failed for model=%s provider=%s",
                self._model_api_name,
                self._provider_id,
            )
        return cost
