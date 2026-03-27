import json
import logging
from decimal import Decimal

import genai_prices
from pydantic_ai import Agent, RunUsage
from pydantic_ai.messages import (
    ModelMessagesTypeAdapter,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
)

from hexa.assistant.instructions import InstructionSet, get_instructions
from hexa.assistant.model_builder import AiModelBuilder
from hexa.assistant.models import Conversation, Message, ToolInvocation

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

    def __init__(self, conversation: Conversation):
        self.conversation = conversation
        builder = AiModelBuilder.from_conversation(conversation)
        self._model_api_name = builder.model_api_name
        self._provider_id = builder.provider_id
        self._model = builder.build()

        self.agent = Agent(
            model=self._model,
            instructions=get_instructions(self.instruction_set),
            tools=self._get_tools(conversation),
        )

    def _get_tools(self, conversation: Conversation) -> list:
        """
        Override in subclasses to provide agent-specific tools.
        Each tool must be a plain function with a docstring (used as the tool description)
        and typed parameters. Use closures to bind conversation context (user, workspace, etc.)
        See PipelineAgent for an example.
        """
        return []

    def run(self, user_input: str) -> str:
        is_first_message = self.conversation.name is None

        Message.objects.create(
            conversation=self.conversation,
            role=Message.Role.USER,
            content=user_input,
        )

        history = ModelMessagesTypeAdapter.validate_python(
            self.conversation.messages_history
        )
        logger.info(
            "agent.run: conversation=%s history_len=%d",
            self.conversation.id,
            len(history),
        )

        result = self.agent.run_sync(user_input, message_history=history)
        logger.info(
            "agent.run: LLM call complete, new_messages=%d", len(result.new_messages())
        )

        response_text = ""
        tool_invocations: dict[str, ToolInvocation] = {}
        for msg in result.new_messages():
            logger.debug(
                "agent.run: processing message type=%s parts=%d",
                type(msg).__name__,
                len(msg.parts),
            )
            for part in msg.parts:
                logger.debug("agent.run: part type=%s", type(part).__name__)
                if isinstance(part, TextPart):
                    response_text += part.content
                elif isinstance(part, ToolCallPart):
                    logger.info(
                        "agent.run: tool_call tool=%s call_id=%s",
                        part.tool_name,
                        part.tool_call_id,
                    )
                    tool_invocations[part.tool_call_id] = ToolInvocation(
                        tool_call_id=part.tool_call_id,
                        tool_name=part.tool_name,
                        tool_input=json.loads(json.dumps(part.args, default=str)),
                    )
                elif isinstance(part, ToolReturnPart):
                    logger.info("agent.run: tool_return call_id=%s", part.tool_call_id)
                    success = _is_success(part.content)
                    tool_output = json.loads(json.dumps(part.content, default=str))
                    try:
                        invocation = tool_invocations[part.tool_call_id]
                        invocation.tool_output = tool_output
                        invocation.success = success
                    except KeyError:
                        tool_invocations[part.tool_call_id] = ToolInvocation(
                            tool_call_id=part.tool_call_id,
                            tool_name=part.tool_name,
                            tool_input="",
                            tool_output=tool_output,
                            success=success,
                        )

        usage = result.usage()
        input_tok = usage.input_tokens or 0
        output_tok = usage.output_tokens or 0
        cost = self._get_cost(usage)

        logger.info(
            "agent.run: usage input_tokens=%d output_tokens=%d cost=%s response_text_len=%d",
            input_tok,
            output_tok,
            cost,
            len(response_text),
        )

        assistant_message = Message.objects.create(
            conversation=self.conversation,
            role=Message.Role.ASSISTANT,
            content=response_text,
            input_tokens=input_tok,
            output_tokens=output_tok,
            cost=cost,
        )
        for tool_invocation in tool_invocations.values():
            tool_invocation.message = assistant_message
            tool_invocation.save()

        self.conversation.total_input_tokens += input_tok
        self.conversation.total_output_tokens += output_tok
        if cost is not None:
            self.conversation.cost += cost
        self.conversation.messages_history = ModelMessagesTypeAdapter.dump_python(
            result.all_messages(), mode="json"
        )

        update_fields = [
            "total_input_tokens",
            "total_output_tokens",
            "cost",
            "messages_history",
            "updated_at",
        ]
        if is_first_message:
            name, naming_usage = self._generate_conversation_name(user_input)
            self.conversation.name = name
            naming_cost = self._get_cost(naming_usage)
            if naming_cost is not None:
                self.conversation.cost += naming_cost
            update_fields.append("name")

        self.conversation.save(update_fields=update_fields)

        return response_text

    def _generate_conversation_name(self, user_input: str) -> tuple[str, RunUsage]:
        naming_agent = Agent(model=self._model, instructions=_NAMING_INSTRUCTIONS)
        try:
            result = naming_agent.run_sync(user_input)
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
