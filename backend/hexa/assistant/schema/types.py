from ariadne import ObjectType

from hexa.assistant.models import Conversation, Message
from hexa.core.graphql import result_page

assistant_conversation_object = ObjectType("AssistantConversation")
assistant_message_object = ObjectType("AssistantMessage")
assistant_tool_invocation_object = ObjectType("AssistantToolInvocation")


@assistant_conversation_object.field("messages")
def resolve_conversation_messages(
    conversation: Conversation, info, page=1, per_page=20, **kwargs
):
    qs = conversation.messages.all()
    return result_page(queryset=qs, page=page, per_page=per_page)


@assistant_message_object.field("toolInvocations")
def resolve_conversation_tool_invocations(message: Message, info, **kwargs):
    return message.tool_invocations.all()


bindables = [
    assistant_conversation_object,
    assistant_message_object,
    assistant_tool_invocation_object,
]
