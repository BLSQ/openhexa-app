from ariadne import ObjectType, QueryType
from django.conf import settings

from hexa.assistant.models import Conversation
from hexa.workspaces.models import Workspace

assistant_queries = QueryType()
workspace_object = ObjectType("Workspace")
me_object = ObjectType("Me")


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
    return Conversation.objects.filter_for_user(request.user).filter(
        workspace=workspace
    )


@me_object.field("assistantMonthlyLimitExceeded")
def resolve_assistant_monthly_limit_exceeded(me, info, **kwargs):
    request = info.context["request"]
    monthly_cost = Conversation.get_monthly_cost_for_user(request.user)
    return monthly_cost >= settings.ASSISTANT_MONTHLY_LIMIT


@me_object.field("assistantMonthlyCost")
def resolve_assistant_monthly_cost(me, info, **kwargs):
    """
    Cost in microdollars (millionths of a dollar) to avoid floating-point precision loss
    """
    request = info.context["request"]
    monthly_cost = Conversation.get_monthly_cost_for_user(request.user)
    return int(monthly_cost * 1_000_000)


@me_object.field("assistantTotalCost")
def resolve_assistant_total_cost(me, info, **kwargs):
    """
    Cost in microdollars (millionths of a dollar) to avoid floating-point precision loss
    """
    request = info.context["request"]
    total_cost = Conversation.get_total_cost_for_user(request.user)
    return int(total_cost * 1_000_000)


bindables = [assistant_queries, workspace_object, me_object]
