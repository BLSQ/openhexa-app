from ariadne import ObjectType, UnionType

from hexa.assistant.models import Conversation, Message
from hexa.assistant.types import TextSegment, ToolSegment
from hexa.core.graphql import result_page

assistant_conversation_object = ObjectType("AssistantConversation")
assistant_message_object = ObjectType("AssistantMessage")
assistant_message_segment_union = UnionType("AssistantMessageSegment")


@assistant_conversation_object.field("messages")
def resolve_conversation_messages(
    conversation: Conversation, info, page=1, per_page=20, **kwargs
):
    qs = conversation.messages.prefetch_related("tool_invocations")
    return result_page(queryset=qs, page=page, per_page=per_page)


@assistant_message_object.field("content")
def resolve_message_content(message: Message, info, **kwargs):
    invocations = {inv.tool_call_id: inv for inv in message.tool_invocations.all()}
    result = []
    for seg in message.content_segments:
        if isinstance(seg, TextSegment):
            result.append({"__typename": "AssistantTextSegment", "content": seg.content})
        elif isinstance(seg, ToolSegment):
            inv = invocations.get(seg.tool_call_id)
            result.append({
                "__typename": "AssistantToolSegment",
                "tool_call_id": seg.tool_call_id,
                "tool_name": inv.tool_name if inv else seg.tool_call_id,
                "tool_input": inv.tool_input if inv else {},
                "tool_output": inv.tool_output if inv else None,
                "success": inv.success if inv else False,
            })
    return result


@assistant_message_segment_union.type_resolver
def resolve_message_segment_type(obj, *_):
    return obj["__typename"]


bindables = [
    assistant_conversation_object,
    assistant_message_object,
    assistant_message_segment_union,
]
