from ariadne import ObjectType, QueryType

from hexa.assistant.models import Conversation
from hexa.workspaces.models import Workspace

assistant_queries = QueryType()
workspace_object = ObjectType("Workspace")


@assistant_queries.field("assistantConversation")
def resolve_assistant_conversation(_, info, id, **kwargs):
    request = info.context["request"]
    try:
        return Conversation.objects.filter_for_user(request.user).get(id=id)
    except Conversation.DoesNotExist:
        return None


@workspace_object.field("assistantConversations")
def resolve_workspace_assistant_conversations(workspace: Workspace, info, **kwargs):
    request = info.context["request"]
    return Conversation.objects.filter_for_user(request.user).filter(workspace=workspace)


bindables = [assistant_queries, workspace_object]
