from ariadne import ObjectType, UnionType

from hexa.assistant.models import Conversation, Message, ToolInvocation
from hexa.assistant.types import TextSegment, ToolSegment
from hexa.core.graphql import result_page

assistant_conversation_object = ObjectType("AssistantConversation")
assistant_message_object = ObjectType("AssistantMessage")
assistant_message_segment_union = UnionType("AssistantMessageSegment")


def tool_segment(inv: ToolInvocation | None, tool_call_id: str) -> dict:
    """Shape a tool invocation as an AssistantToolSegment payload.

    The single place tool segments are built for GraphQL — message history and
    the resolveAssistantProposal mutation both go through here, so the `tool`
    coercion below happens exactly once. `tool` is the typed view of `tool_name`:
    null when the stored name is not a known tool (an old conversation that used
    a since-removed tool, or a segment whose invocation record is missing), so
    historical data degrades gracefully instead of breaking enum serialization.
    """
    # Deferred import: `agents` pulls in `hexa.mcp.tools`, which imports the
    # assembled GraphQL schema — importing it at module load would create a cycle.
    from hexa.assistant.agents import all_agent_tool_names

    tool_name = inv.tool_name if inv else tool_call_id
    return {
        "__typename": "AssistantToolSegment",
        "id": str(inv.id) if inv else None,
        "tool_call_id": tool_call_id,
        "tool_name": tool_name,
        "tool": tool_name if tool_name in all_agent_tool_names() else None,
        "tool_input": inv.tool_input if inv else {},
        "tool_output": inv.tool_output if inv else None,
        "success": inv.success if inv else False,
        "proposal_pending": inv.proposal_pending if inv else False,
    }


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
            result.append(tool_segment(inv, seg.tool_call_id))
    return result


@assistant_message_segment_union.type_resolver
def resolve_message_segment_type(obj, *_):
    return obj["__typename"]


bindables = [
    assistant_conversation_object,
    assistant_message_object,
    assistant_message_segment_union,
]
