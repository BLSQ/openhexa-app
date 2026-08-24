from ariadne import QueryType

from hexa.core.graphql import result_page
from hexa.tags.models import InvalidTag, Tag

from ..models import (
    Connection,
    Workspace,
    WorkspaceInvitation,
    WorkspaceInvitationStatus,
)

workspace_queries = QueryType()


@workspace_queries.field("workspaces")
def resolve_workspaces(
    _, info, query=None, organization_id=None, tags=None, page=1, per_page=15
):
    request = info.context["request"]
    queryset = (
        Workspace.objects.filter_for_user(request.user)
        .select_related("organization")
        .prefetch_related("tags")
        .order_by("name")
    )
    if organization_id:
        queryset = queryset.filter(organization_id=organization_id)
    if query:
        queryset = queryset.filter_by_query(query)
    if tags:
        try:
            queryset = queryset.filter_by_tags(Tag.from_names(tags))
        except InvalidTag:
            queryset = Workspace.objects.none()

    result = result_page(queryset=queryset, page=page, per_page=per_page)
    Workspace.preload_memberships(request.user, result["items"])
    return result


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


@workspace_queries.field("connectionBySlug")
def resolve_workspace_connection_by_slug(_, info, **kwargs):
    request = info.context["request"]
    try:
        return Connection.objects.filter_for_user(request.user).get(
            workspace__slug=kwargs["workspace_slug"], slug=kwargs["connection_slug"]
        )
    except Connection.DoesNotExist:
        return None


@workspace_queries.field("pendingWorkspaceInvitations")
def resolve_pending_workspace_invitations(_, info, page=1, per_page=10):
    request = info.context["request"]
    if not request.user.is_authenticated:
        qs = WorkspaceInvitation.objects.none()
    else:
        qs = WorkspaceInvitation.objects.filter(
            email=request.user.email, status=WorkspaceInvitationStatus.PENDING
        ).order_by("-created_at")
    return result_page(qs, page=page, per_page=per_page)


bindables = [
    workspace_queries,
]
