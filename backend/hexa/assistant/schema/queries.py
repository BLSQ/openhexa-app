from ariadne import ObjectType, QueryType
from django.contrib.contenttypes.models import ContentType

from hexa.assistant.models import Conversation
from hexa.pipelines.models import Pipeline
from hexa.pipelines.schema.types import pipeline_object
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


@pipeline_object.field("assistantConversations")
def resolve_pipeline_assistant_conversations(pipeline: Pipeline, info, **kwargs):
    request = info.context["request"]
    ct = ContentType.objects.get_for_model(Pipeline)
    return Conversation.objects.filter_for_user(request.user).filter(
        linked_object_content_type=ct, linked_object_id=pipeline.id, user=request.user
    )


@me_object.field("assistantMonthlyLimitExceeded")
def resolve_assistant_monthly_limit_exceeded(me, info, **kwargs):
    request = info.context["request"]
    monthly_cost = Conversation.get_monthly_cost_for_user(request.user)
    return monthly_cost >= request.user.ai_settings_safe.effective_monthly_limit()


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


@me_object.field("assistantMonthlyLimit")
def resolve_assistant_monthly_limit(me, info, **kwargs):
    """
    Effective monthly cap in microdollars. Per-user for managed providers, global otherwise.
    """
    request = info.context["request"]
    monthly_limit = request.user.ai_settings_safe.effective_monthly_limit()
    return int(monthly_limit * 1_000_000)


bindables = [assistant_queries, workspace_object, me_object]
