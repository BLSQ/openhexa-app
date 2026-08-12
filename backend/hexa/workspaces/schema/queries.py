from ariadne import QueryType
from django.db.models import Prefetch

from hexa.core.graphql import result_page

from ..models import (
    Connection,
    Workspace,
    WorkspaceInvitation,
    WorkspaceInvitationStatus,
    WorkspaceMembership,
)

workspace_queries = QueryType()


@workspace_queries.field("workspaces")
def resolve_workspaces(
    _,
    info,
    query=None,
    organization_id=None,
    with_current_membership=False,
    page=1,
    per_page=15,
):
    request = info.context["request"]
    queryset = Workspace.objects.filter_for_user(request.user).order_by("name")
    if request.user.is_authenticated:
        # Without this, resolving `currentMembership` costs one query per workspace
        queryset = queryset.prefetch_related(
            Prefetch(
                "workspacemembership_set",
                # access_token is deferred: it is a secret and is only ever read
                # through the generateWorkspaceToken mutation, never from here.
                queryset=WorkspaceMembership.objects.filter(user=request.user).defer(
                    "access_token"
                ),
                to_attr="current_user_memberships",
            )
        )
        if with_current_membership:
            # filter_for_user also returns workspaces reachable through an
            # organization admin/owner role (and every workspace for superusers),
            # where the user has no membership at all.
            queryset = queryset.filter(workspacemembership__user=request.user)
    if organization_id:
        queryset = queryset.filter(organization_id=organization_id)
    if query:
        queryset = queryset.filter(name__icontains=query)
    return result_page(queryset=queryset, page=page, per_page=per_page)


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
        return []
    qs = WorkspaceInvitation.objects.filter(
        email=request.user.email, status=WorkspaceInvitationStatus.PENDING
    ).order_by("-created_at")
    return result_page(qs, page=page, per_page=per_page)


bindables = [
    workspace_queries,
]
