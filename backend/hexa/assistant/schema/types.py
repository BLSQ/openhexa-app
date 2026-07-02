from ariadne import ObjectType, UnionType

from hexa.assistant.models import Conversation, Message
from hexa.assistant.types import TextSegment, ToolSegment
from hexa.core.graphql import result_page

assistant_conversation_object = ObjectType("AssistantConversation")
assistant_message_object = ObjectType("AssistantMessage")
assistant_tool_segment_object = ObjectType("AssistantToolSegment")
assistant_message_segment_union = UnionType("AssistantMessageSegment")


@assistant_tool_segment_object.field("tool")
def resolve_tool_segment_tool(obj, info):
    # Deferred import: `agents` pulls in `hexa.mcp.tools`, which imports the
    # assembled GraphQL schema — importing it at module load would create a cycle.
    from hexa.assistant.agents import all_agent_tool_names

    tool_name = (
        obj.get("tool_name") if isinstance(obj, dict) else getattr(obj, "tool_name", None)
    )
    return tool_name if tool_name in all_agent_tool_names() else None


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
            result.append(
                {"__typename": "AssistantTextSegment", "content": seg.content}
            )
        elif isinstance(seg, ToolSegment):
            inv = invocations.get(seg.tool_call_id)
            result.append(
                {
                    "__typename": "AssistantToolSegment",
                    "id": str(inv.id) if inv else None,
                    "tool_call_id": seg.tool_call_id,
                    "tool_name": inv.tool_name if inv else seg.tool_call_id,
                    "tool_input": inv.tool_input if inv else {},
                    "tool_output": inv.tool_output if inv else None,
                    "success": inv.success if inv else False,
                    "proposal_pending": inv.proposal_pending if inv else False,
                }
            )
    return result


@assistant_message_segment_union.type_resolver
def resolve_message_segment_type(obj, *_):
    return obj["__typename"]


bindables = [
    assistant_conversation_object,
    assistant_message_object,
    assistant_tool_segment_object,
    assistant_message_segment_union,
]
