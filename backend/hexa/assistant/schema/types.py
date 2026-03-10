from ariadne import ObjectType

from hexa.assistant.models import Conversation
from hexa.core.graphql import result_page

assistant_conversation_object = ObjectType("AssistantConversation")
assistant_message_object = ObjectType("AssistantMessage")
assistant_tool_invocation_object = ObjectType("AssistantToolInvocation")


@assistant_conversation_object.field("messages")
def resolve_conversation_messages(conversation: Conversation, info, page=1, perPage=20, **kwargs):
    qs = conversation.messages.order_by("-created_at")
    return result_page(queryset=qs, page=page, per_page=perPage)


@assistant_conversation_object.field("toolInvocations")
def resolve_conversation_tool_invocations(conversation: Conversation, info, **kwargs):
    return conversation.tool_invocations.all()


@assistant_conversation_object.field("cost")
def resolve_conversation_cost(conversation: Conversation, info, **kwargs):
    return float(conversation.cost)


bindables = [
    assistant_conversation_object,
    assistant_message_object,
    assistant_tool_invocation_object,
]
