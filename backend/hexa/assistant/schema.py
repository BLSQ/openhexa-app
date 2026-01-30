import logging
import pathlib

from ariadne import MutationType, ObjectType, QueryType, load_schema_from_path
from django.http import HttpRequest

from hexa.workspaces.models import Workspace

from .models import ASSISTANT_MODELS, Conversation, Message, PendingToolApproval, ToolExecution

logger = logging.getLogger(__name__)

assistant_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

assistant_query = QueryType()
workspace_object = ObjectType("Workspace")
conversation_object = ObjectType("AssistantConversation")
assistant_mutations = MutationType()


@assistant_query.field("assistantModels")
def resolve_assistant_models(_, info):
    return [
        {"id": model_id, "label": config["label"]}
        for model_id, config in ASSISTANT_MODELS.items()
    ]


@workspace_object.field("assistantEnabled")
def resolve_workspace_assistant_enabled(workspace: Workspace, info):
    return (
        workspace.organization is not None and workspace.organization.assistant_enabled
    )


@workspace_object.field("assistantConversations")
def resolve_workspace_assistant_conversations(workspace: Workspace, info):
    request: HttpRequest = info.context["request"]
    return Conversation.objects.filter(workspace=workspace, user=request.user).order_by(
        "-updated_at"
    )


@conversation_object.field("messages")
def resolve_conversation_messages(conversation: Conversation, info):
    messages = list(conversation.messages.all())
    tool_executions = list(conversation.tool_executions.all())

    merged = messages + [
        _tool_execution_as_message(te) for te in tool_executions
    ]
    merged.sort(key=lambda m: m.created_at if hasattr(m, "created_at") else m["created_at"])
    return merged


def _tool_execution_as_message(te: ToolExecution) -> dict:
    return {
        "id": te.id,
        "role": "tool_use",
        "content": "",
        "created_at": te.created_at,
        "input_tokens": None,
        "output_tokens": None,
        "cost": None,
        "tool_name": te.tool_name,
        "tool_input": te.tool_input,
    }


@conversation_object.field("estimatedCost")
def resolve_estimated_cost(conversation: Conversation, info):
    return float(conversation.estimated_cost)


@assistant_mutations.field("sendAssistantMessage")
def resolve_send_assistant_message(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input_data = kwargs["input"]
    workspace_slug = input_data["workspace_slug"]
    message_text = input_data["message"]
    conversation_id = input_data.get("conversation_id")

    if not message_text or not message_text.strip():
        return {
            "success": False,
            "status": "COMPLETE",
            "errors": ["EMPTY_MESSAGE"],
            "message": None,
            "usage": None,
            "pending_tool_call": None,
        }

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=workspace_slug
        )
    except Workspace.DoesNotExist:
        return {
            "success": False,
            "status": "COMPLETE",
            "errors": ["PERMISSION_DENIED"],
            "message": None,
            "usage": None,
            "pending_tool_call": None,
        }

    if not (workspace.organization and workspace.organization.assistant_enabled):
        return {
            "success": False,
            "status": "COMPLETE",
            "errors": ["ASSISTANT_DISABLED"],
            "message": None,
            "usage": None,
            "pending_tool_call": None,
        }

    if conversation_id:
        try:
            conversation = Conversation.objects.get(
                id=conversation_id, workspace=workspace, user=request.user
            )
        except Conversation.DoesNotExist:
            return {
                "success": False,
                "status": "COMPLETE",
                "errors": ["CONVERSATION_NOT_FOUND"],
                "message": None,
                "usage": None,
                "pending_tool_call": None,
            }
    else:
        conversation = Conversation.objects.create(
            user=request.user, workspace=workspace
        )

    try:
        from .agent import AgentService

        agent = AgentService(workspace, conversation)
        result = agent.send_message(message_text)
    except Exception:
        logger.exception("Agent error in conversation %s", conversation.id)
        return {
            "success": False,
            "status": "COMPLETE",
            "errors": ["AGENT_ERROR"],
            "message": None,
            "usage": None,
            "pending_tool_call": None,
        }

    if result.get("status") == "awaiting_approval":
        return {
            "success": True,
            "status": "AWAITING_APPROVAL",
            "errors": [],
            "message": None,
            "usage": result["usage"],
            "pending_tool_call": result["pending_tool"],
        }

    assistant_message = conversation.messages.filter(role="assistant").last()

    return {
        "success": True,
        "status": "COMPLETE",
        "errors": [],
        "message": assistant_message,
        "usage": result["usage"],
        "pending_tool_call": None,
    }


@assistant_mutations.field("approveToolExecution")
def resolve_approve_tool_execution(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input_data = kwargs["input"]
    pending_id = input_data["pending_tool_call_id"]
    approved = input_data["approved"]

    try:
        pending = PendingToolApproval.objects.select_related(
            "conversation", "conversation__workspace"
        ).get(
            id=pending_id,
            conversation__user=request.user,
            status="pending",
        )
    except PendingToolApproval.DoesNotExist:
        return {
            "success": False,
            "status": "COMPLETE",
            "errors": ["NOT_FOUND"],
            "message": None,
            "usage": None,
            "pending_tool_call": None,
        }

    if not approved:
        pending.status = "rejected"
        pending.save()

        Message.objects.create(
            conversation=pending.conversation,
            role="assistant",
            content="Tool execution was not approved. How else can I help you?",
        )

        return {
            "success": True,
            "status": "COMPLETE",
            "message": pending.conversation.messages.filter(role="assistant").last(),
            "errors": [],
            "usage": {
                "input_tokens": pending.input_tokens_so_far,
                "output_tokens": pending.output_tokens_so_far,
                "cost": 0,
            },
            "pending_tool_call": None,
        }

    pending.status = "approved"
    pending.save()

    try:
        from .agent import AgentService

        agent = AgentService(pending.conversation.workspace, pending.conversation)
        result = agent.resume_after_approval(pending)
    except Exception:
        logger.exception("Agent error resuming approval %s", pending.id)
        return {
            "success": False,
            "status": "COMPLETE",
            "errors": ["AGENT_ERROR"],
            "message": None,
            "usage": None,
            "pending_tool_call": None,
        }

    if result.get("status") == "awaiting_approval":
        return {
            "success": True,
            "status": "AWAITING_APPROVAL",
            "errors": [],
            "message": None,
            "usage": result["usage"],
            "pending_tool_call": result["pending_tool"],
        }

    return {
        "success": True,
        "status": "COMPLETE",
        "message": pending.conversation.messages.filter(role="assistant").last(),
        "errors": [],
        "usage": result["usage"],
        "pending_tool_call": None,
    }


@assistant_mutations.field("deleteAssistantConversation")
def resolve_delete_assistant_conversation(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input_data = kwargs["input"]

    try:
        conversation = Conversation.objects.filter_for_user(request.user).get(
            id=input_data["id"]
        )
    except Conversation.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}

    conversation.delete()
    return {"success": True, "errors": []}


assistant_bindables = [
    assistant_query,
    workspace_object,
    conversation_object,
    assistant_mutations,
]
