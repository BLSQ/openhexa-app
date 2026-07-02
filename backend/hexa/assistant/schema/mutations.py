from logging import getLogger

from ariadne import MutationType
from django.core.exceptions import PermissionDenied

from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, ToolInvocation
from hexa.pipelines.models import Pipeline
from hexa.webapps.models import GitWebapp
from hexa.workspaces.models import Workspace

logger = getLogger(__name__)
assistant_mutations = MutationType()


def _resolve_linked_object(user, linked_object_type, linked_object_id):
    """
    Maps a (type, id) pair from the API to a model instance and the instruction set
    that should be used for conversations about that object type.
    Returns (linked_object, instruction_set) or raises ValueError/DoesNotExist.
    """
    resolvers = {
        "Pipeline": (
            Pipeline.objects.filter_for_user(user),
            InstructionSet.EDIT_PIPELINE,
        ),
        "StaticWebapp": (
            GitWebapp.objects.filter_for_user(user),
            InstructionSet.EDIT_WEBAPP,
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


@assistant_mutations.field("resolveAssistantProposal")
def resolve_assistant_proposal(_, info, tool_invocation_id, **kwargs):
    request = info.context["request"]
    try:
        invocation = ToolInvocation.objects.select_related("message__conversation").get(
            id=tool_invocation_id
        )
    except ToolInvocation.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}

    if invocation.message.conversation.user != request.user:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}

    invocation.proposal_pending = False
    invocation.save(update_fields=["proposal_pending"])

    ToolInvocation.objects.filter(
        message__conversation=invocation.message.conversation,
        tool_name=invocation.tool_name,
        proposal_pending=True,
    ).update(proposal_pending=False)

    return {"success": True, "errors": [], "toolInvocation": invocation}


bindables = [assistant_mutations]
