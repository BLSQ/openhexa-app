from pydantic_ai import Agent
from pydantic_ai.messages import (
    ModelMessagesTypeAdapter,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
)

from hexa.assistant.models import Conversation, Message, ToolInvocation


class AssistantAgent:
    def __init__(self, conversation: Conversation):
        self.conversation = conversation
        self.agent = Agent(model=conversation.model)

    def run(self, user_input: str) -> str:
        history = ModelMessagesTypeAdapter.validate_python(
            self.conversation.messages_history
        )

        result = self.agent.run_sync(user_input, message_history=history)

        Message.objects.create(
            conversation=self.conversation,
            role=Message.Role.USER,
            content=user_input,
        )

        response_text = ""
        for msg in result.new_messages():
            for part in msg.parts:
                if isinstance(part, TextPart):
                    response_text += part.content
                elif isinstance(part, ToolCallPart):
                    ToolInvocation.objects.create(
                        conversation=self.conversation,
                        tool_call_id=part.tool_call_id,
                        tool_name=part.tool_name,
                        tool_input=part.args,
                    )
                elif isinstance(part, ToolReturnPart):
                    ToolInvocation.objects.filter(
                        conversation=self.conversation,
                        tool_call_id=part.tool_call_id,
                    ).update(tool_output=part.content)

        usage = result.usage()
        input_tok = usage.request_tokens or 0
        output_tok = usage.response_tokens or 0

        Message.objects.create(
            conversation=self.conversation,
            role=Message.Role.ASSISTANT,
            content=response_text,
            input_tokens=input_tok,
            output_tokens=output_tok,
        )

        self.conversation.total_input_tokens += input_tok
        self.conversation.total_output_tokens += output_tok
        self.conversation.messages_history = ModelMessagesTypeAdapter.dump_python(
            result.all_messages(), mode="json"
        )
        self.conversation.save(
            update_fields=[
                "total_input_tokens",
                "total_output_tokens",
                "messages_history",
                "updated_at",
            ]
        )

        return response_text
