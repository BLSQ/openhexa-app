from ariadne import MutationType
from django.conf import settings

from hexa.assistant.agent import AssistantAgent
from hexa.assistant.models import Conversation
from hexa.workspaces.models import Workspace

assistant_mutations = MutationType()


@assistant_mutations.field("createAssistantConversation")
def resolve_create_assistant_conversation(_, info, input, **kwargs):
    request = info.context["request"]

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=input["workspace_slug"]
        )
    except Workspace.DoesNotExist:
        return None

    return Conversation.objects.create(
        user=request.user,
        workspace=workspace,
    )


@assistant_mutations.field("sendAssistantMessage")
def resolve_send_assistant_message(_, info, input, **kwargs):
    request = info.context["request"]

    try:
        conversation = Conversation.objects.filter_for_user(request.user).get(
            id=input["conversation_id"]
        )
    except Conversation.DoesNotExist:
        return {
            "success": False,
            "errors": ["CONVERSATION_NOT_FOUND"],
            "conversation": None,
            "message": None,
        }

    monthly_cost = Conversation.get_monthly_cost_for_user(request.user)
    if monthly_cost >= settings.ASSISTANT_MONTHLY_LIMIT:
        return {
            "success": False,
            "errors": ["MONTHLY_LIMIT_EXCEEDED"],
            "conversation": conversation,
            "message": None,
        }

    try:
        agent = AssistantAgent(conversation)
        agent.run(input["message"])
    except Exception as e:
        return {
            "success": False,
            "errors": [str(e)],
            "conversation": conversation,
            "message": None,
        }

    last_message = conversation.messages.filter(role="assistant").last()
    return {
        "success": True,
        "errors": [],
        "conversation": conversation,
        "message": last_message,
    }


bindables = [assistant_mutations]
