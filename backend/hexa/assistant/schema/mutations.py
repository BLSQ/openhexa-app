from logging import getLogger

from ariadne import MutationType
from django.conf import settings
from django.core.exceptions import PermissionDenied

from hexa.assistant.agent import AssistantAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation
from hexa.workspaces.models import Workspace

logger = getLogger(__name__)
assistant_mutations = MutationType()


@assistant_mutations.field("createAssistantConversation")
def resolve_create_assistant_conversation(_, info, input, **kwargs):
    request = info.context["request"]

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=input["workspace_slug"]
        )
    except Workspace.DoesNotExist:
        return {"success": False, "errors": ["WORKSPACE_NOT_FOUND"], "conversation": None}

    raw_instruction_set = input.get("instruction_set", InstructionSet.GENERAL)
    try:
        instruction_set = InstructionSet(raw_instruction_set)
    except ValueError:
        logger.warning("Invalid instruction set %s", raw_instruction_set)
        return {"success": False, "errors": ["INVALID_INSTRUCTION_SET"], "conversation": None}

    try:
        conversation = Conversation.objects.create_if_has_perm(
            principal=request.user,
            workspace=workspace,
            instruction_set=instruction_set,
        )
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"], "conversation": None}

    return {"success": True, "errors": [], "conversation": conversation}


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
    if monthly_cost >= settings.ASSISTANT_MONTHLY_LIMIT * 1_000_000:
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
        logger.exception("Failed to send assistant message", exc_info=e)
        return {
            "success": False,
            "errors": ["UNKNOWN_ERROR"],
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
