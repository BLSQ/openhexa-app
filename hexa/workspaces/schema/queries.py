from ariadne import QueryType

from hexa.core.graphql import result_page

from ..models import Connection, Workspace

workspace_queries = QueryType()


@workspace_queries.field("workspaces")
def resolve_workspaces(_, info, query=None, page=1, perPage=15):
    request = info.context["request"]
    queryset = Workspace.objects.filter_for_user(request.user).order_by("-updated_at")
    if query is not None:
        queryset = queryset.filter(name__icontains=query)
    return result_page(queryset=queryset, page=page, per_page=perPage)


@workspace_queries.field("workspace")
def resolve_workspace(_, info, **kwargs):
    request = info.context["request"]
    try:
        return Workspace.objects.filter_for_user(request.user).get(slug=kwargs["slug"])
    except Workspace.DoesNotExist:
        return None


@workspace_queries.field("connection")
def resolve_workspace_connection(_, info, id):
    request = info.context["request"]
    try:
        return Connection.objects.filter_for_user(request.user).get(id=id)
    except Connection.DoesNotExist:
        return None


bindables = [
    workspace_queries,
]
