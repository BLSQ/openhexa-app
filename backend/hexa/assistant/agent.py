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

from hexa.assistant.model_builder import AiModelBuilder
from hexa.assistant.models import Conversation, Message, ToolInvocation

logger = logging.getLogger(__name__)


class AssistantAgent:
    def __init__(self, conversation: Conversation):
        self.conversation = conversation
        builder = AiModelBuilder.from_conversation(conversation)
        self._model_api_name = builder.model_api_name
        self._provider_id = builder.provider_id
        self.agent = Agent(model=builder.build())

    def run(self, user_input: str) -> str:
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

        Message.objects.create(
            conversation=self.conversation,
            role=Message.Role.USER,
            content=user_input,
        )

        response_text = ""
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
                    ToolInvocation.objects.create(
                        conversation=self.conversation,
                        tool_call_id=part.tool_call_id,
                        tool_name=part.tool_name,
                        tool_input=part.args,
                    )
                elif isinstance(part, ToolReturnPart):
                    logger.info("agent.run: tool_return call_id=%s", part.tool_call_id)
                    ToolInvocation.objects.filter(
                        conversation=self.conversation,
                        tool_call_id=part.tool_call_id,
                    ).update(tool_output=part.content)

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

        Message.objects.create(
            conversation=self.conversation,
            role=Message.Role.ASSISTANT,
            content=response_text,
            input_tokens=input_tok,
            output_tokens=output_tok,
            cost=cost,
        )

        self.conversation.total_input_tokens += input_tok
        self.conversation.total_output_tokens += output_tok
        if cost is not None:
            self.conversation.cost += cost
        self.conversation.messages_history = ModelMessagesTypeAdapter.dump_python(
            result.all_messages(), mode="json"
        )
        self.conversation.save(
            update_fields=[
                "total_input_tokens",
                "total_output_tokens",
                "cost",
                "messages_history",
                "updated_at",
            ]
        )

        return response_text

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
