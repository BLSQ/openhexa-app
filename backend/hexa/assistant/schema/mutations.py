from logging import getLogger

from ariadne import MutationType
from django.conf import settings
from django.core.exceptions import PermissionDenied

from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation
from hexa.workspaces.models import Workspace

logger = getLogger(__name__)
assistant_mutations = MutationType()


def _resolve_linked_object(user, linked_object_type, linked_object_id):
    """
    Maps a (type, id) pair from the API to a model instance and the instruction set
    that should be used for conversations about that object type.
    Returns (linked_object, instruction_set) or raises ValueError/DoesNotExist.
    """
    from hexa.pipelines.models import Pipeline

    resolvers = {
        "Pipeline": (
            Pipeline.objects.filter_for_user(user),
            InstructionSet.EDIT_PIPELINE,
        ),
    }
    if linked_object_type not in resolvers:
        raise ValueError(f"Unknown linked object type: {linked_object_type}")
    queryset, instruction_set = resolvers[linked_object_type]
    return queryset.get(id=linked_object_id), instruction_set


@assistant_mutations.field("createAssistantConversation")
def resolve_create_assistant_conversation(_, info, input, **kwargs):
    request = info.context["request"]

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=input["workspace_slug"]
        )
    except Workspace.DoesNotExist:
        return {
            "success": False,
            "errors": ["WORKSPACE_NOT_FOUND"],
            "conversation": None,
        }

    linked_object = None
    if linked_object_id := input.get("linked_object_id"):
        linked_object_type = input.get("linked_object_type", "")
        try:
            linked_object, instruction_set = _resolve_linked_object(
                request.user, linked_object_type, linked_object_id
            )
        except ValueError:
            return {
                "success": False,
                "errors": ["INVALID_LINKED_OBJECT_TYPE"],
                "conversation": None,
            }
        except Exception:
            return {
                "success": False,
                "errors": ["LINKED_OBJECT_NOT_FOUND"],
                "conversation": None,
            }
    else:
        raw_instruction_set = input.get("instruction_set", InstructionSet.GENERAL)
        try:
            instruction_set = InstructionSet(raw_instruction_set)
        except ValueError:
            logger.warning("Invalid instruction set %s", raw_instruction_set)
            return {
                "success": False,
                "errors": ["INVALID_INSTRUCTION_SET"],
                "conversation": None,
            }

    try:
        conversation = Conversation.objects.create_if_has_perm(
            principal=request.user,
            workspace=workspace,
            instruction_set=instruction_set,
            linked_object=linked_object,
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
    if monthly_cost >= settings.ASSISTANT_MONTHLY_LIMIT:
        return {
            "success": False,
            "errors": ["MONTHLY_LIMIT_EXCEEDED"],
            "conversation": conversation,
            "message": None,
        }

    try:
        conversation.agent.run(input["message"])
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
