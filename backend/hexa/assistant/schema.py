import logging
import pathlib

from ariadne import MutationType, ObjectType, QueryType, load_schema_from_path
from django.http import HttpRequest

from hexa.workspaces.models import Workspace

from .models import ASSISTANT_MODELS, Conversation

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
        workspace.organization is not None
        and workspace.organization.assistant_enabled
    )


@workspace_object.field("assistantConversations")
def resolve_workspace_assistant_conversations(workspace: Workspace, info):
    request: HttpRequest = info.context["request"]
    return Conversation.objects.filter(
        workspace=workspace, user=request.user
    ).order_by("-updated_at")


@conversation_object.field("messages")
def resolve_conversation_messages(conversation: Conversation, info):
    return conversation.messages.all()


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
        return {"success": False, "errors": ["EMPTY_MESSAGE"], "message": None, "usage": None}

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(slug=workspace_slug)
    except Workspace.DoesNotExist:
        return {"success": False, "errors": ["PERMISSION_DENIED"], "message": None, "usage": None}

    if not (workspace.organization and workspace.organization.assistant_enabled):
        return {"success": False, "errors": ["ASSISTANT_DISABLED"], "message": None, "usage": None}

    if conversation_id:
        try:
            conversation = Conversation.objects.get(
                id=conversation_id, workspace=workspace, user=request.user
            )
        except Conversation.DoesNotExist:
            return {
                "success": False,
                "errors": ["CONVERSATION_NOT_FOUND"],
                "message": None,
                "usage": None,
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
        return {"success": False, "errors": ["AGENT_ERROR"], "message": None, "usage": None}

    assistant_message = conversation.messages.filter(role="assistant").last()

    return {
        "success": True,
        "errors": [],
        "message": assistant_message,
        "usage": result["usage"],
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
