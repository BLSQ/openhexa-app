from ariadne import MutationType

from hexa.assistant.agent import AssistantAgent
from hexa.assistant.models import Conversation
from hexa.user_management.models import AiSettings, User
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

    model = input.get("model")
    if not model:
        user: User = request.user
        ai_settings: AiSettings = user.ai_settings_safe
        if ai_settings.model:
            model = ai_settings.model
        else:
            return {"success": False, "errors": ["INCOMPLETE_CONFIG"]}

    return Conversation.objects.create(
        user=request.user,
        workspace=workspace,
        model=model,
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
