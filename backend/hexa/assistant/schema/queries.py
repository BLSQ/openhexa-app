from ariadne import ObjectType, QueryType
from django.contrib.contenttypes.models import ContentType

from hexa.assistant.models import Conversation
from hexa.data_studio.models import SavedQuery
from hexa.data_studio.schema import saved_query_object
from hexa.pipelines.models import Pipeline
from hexa.pipelines.schema.types import pipeline_object
from hexa.webapps.models import GitWebapp
from hexa.webapps.schema.types import webapp_object
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


@webapp_object.field("assistantConversations")
def resolve_webapp_assistant_conversations(webapp: GitWebapp, info, **kwargs):
    request = info.context["request"]
    ct = ContentType.objects.get_for_model(GitWebapp)
    return Conversation.objects.filter_for_user(request.user).filter(
        linked_object_content_type=ct, linked_object_id=webapp.id, user=request.user
    )


@saved_query_object.field("assistantConversations")
def resolve_saved_query_assistant_conversations(
    saved_query: SavedQuery, info, **kwargs
):
    request = info.context["request"]
    ct = ContentType.objects.get_for_model(SavedQuery)
    return Conversation.objects.filter_for_user(request.user).filter(
        linked_object_content_type=ct,
        linked_object_id=saved_query.id,
        user=request.user,
    )


bindables = [assistant_queries, workspace_object]
