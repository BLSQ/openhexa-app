import logging

from ariadne import EnumType, InterfaceType, ObjectType
from django.db.models import OuterRef, Subquery
from django.http import HttpRequest
from openhexa.toolbox.dhis2.api import DHIS2ToolboxError
from openhexa.toolbox.iaso.api_client import IASOError

from hexa.core.graphql import result_page
from hexa.pipelines.authentication import PipelineRunUser
from hexa.pipelines.models import Pipeline, PipelineRun
from hexa.tags.models import Tag
from hexa.user_management.models import OrganizationMembership
from hexa.user_management.schema import me_permissions_object

from ..models import (
    Connection,
    ConnectionField,
    Workspace,
    WorkspaceInvitation,
    WorkspaceInvitationStatus,
    WorkspaceMembership,
)
from ..utils import (
    DHIS2MetadataQueryType,
    IASOMetadataQueryType,
    query_dhis2_metadata,
    query_iaso_metadata,
    toolbox_client_from_connection,
)

workspace_object = ObjectType("Workspace")
workspace_permissions = ObjectType("WorkspacePermissions")
workspace_membership_object = ObjectType("WorkspaceMembership")
connection_interface = InterfaceType("Connection")
connection_field_object = ObjectType("ConnectionField")
connection_permissions_object = ObjectType("ConnectionPermissions")
dhis2_connection = ObjectType("DHIS2Connection")
dhis2_metadata_type = EnumType("DHIS2MetadataType", DHIS2MetadataQueryType)
iaso_connection = ObjectType("IASOConnection")
iaso_metadata_type = EnumType("IASOMetadataType", IASOMetadataQueryType)


@connection_permissions_object.field("update")
def resolve_connection_permissions_update(connection: Connection, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("workspaces.update_connection", connection)


@connection_permissions_object.field("delete")
def resolve_connection_permissions_delete(connection: Connection, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("workspaces.delete_connection", connection)


@workspace_permissions.field("createConnection")
def resolve_workspace_permissions_create_connection(obj: Workspace, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("workspaces.create_connection", obj)
        if request.user.is_authenticated
        else False
    )


@workspace_permissions.field("deleteDatabaseTable")
def resolve_workspace_permissions_delete_table(obj: Workspace, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("workspaces.delete_database_table", obj)
        if request.user.is_authenticated
        else False
    )


@me_permissions_object.field("createWorkspace")
def resolve_me_permissions_create_workspace(me, info):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("user_management.create_workspace")
        if request.user.is_authenticated
        else False
    )


@workspace_permissions.field("update")
def resolve_workspace_permission_update(workspace: Workspace, info):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("workspaces.update_workspace", workspace)
        if request.user.is_authenticated
        else False
    )


@workspace_permissions.field("delete")
def resolve_workspace_permission_delete(workspace: Workspace, info):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("workspaces.delete_workspace", workspace)
        if request.user.is_authenticated
        else False
    )


@workspace_permissions.field("manageMembers")
def resolve_workspace_permission_manage(workspace: Workspace, info):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("workspaces.manage_members", workspace)
        if request.user.is_authenticated
        else False
    )


@workspace_permissions.field("launchNotebookServer")
def resolve_workspace_permission_launch_notebooks(workspace: Workspace, info):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("workspaces.launch_notebooks", workspace)
        if request.user.is_authenticated
        else False
    )


@workspace_object.field("permissions")
def resolve_workspace_permissions(workspace: Workspace, info):
    return workspace


@connection_interface.field("permissions")
def resolve_workspace_connection_permissions(connection: Connection, info):
    return connection


@workspace_object.field("countries")
def resolve_workspace_countries(workspace: Workspace, info, **kwargs):
    if workspace.countries is not None:
        return workspace.countries
    return []


@workspace_object.field("organization")
def resolve_workspace_organization(workspace: Workspace, info):
    return workspace.organization


@workspace_object.field("members")
def resolve_workspace_members(workspace: Workspace, info, **kwargs):
    request: HttpRequest = info.context["request"]

    # Return empty result if user doesn't have manageMembers permission
    if not request.user.has_perm("workspaces.manage_members", workspace):
        return result_page(
            queryset=workspace.workspacemembership_set.none(),
            page=kwargs.get("page", 1),
            per_page=kwargs.get("per_page", 10),
        )

    qs = workspace.workspacemembership_set.all().order_by("-updated_at")
    return result_page(
        queryset=qs,
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", qs.count() or 10),
    )


@workspace_object.field("invitations")
def resolve_workspace_invitations(workspace: Workspace, info, **kwargs):
    request: HttpRequest = info.context["request"]

    qs = (
        WorkspaceInvitation.objects.filter_for_user(request.user)
        .filter(workspace=workspace)
        .order_by("-updated_at")
    )
    if not kwargs.get("include_accepted"):
        qs = qs.exclude(status=WorkspaceInvitationStatus.ACCEPTED)

    return result_page(
        queryset=qs,
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", 5),
    )


@workspace_object.field("shortcuts")
def resolve_workspace_shortcuts(workspace: Workspace, info, **kwargs):
    from hexa.shortcuts.models import Shortcut

    request: HttpRequest = info.context["request"]
    shortcuts = (
        Shortcut.objects.filter_for_user(request.user)
        .filter(workspace=workspace)
        .order_by("order", "created_at")
    )
    return [
        item
        for shortcut in shortcuts
        if (item := shortcut.to_shortcut_item()) is not None
    ]


@workspace_object.field("connections")
def resolve_workspace_connections(workspace: Workspace, info, **kwargs):
    return workspace.connections.all()


@workspace_object.field("pipelineTags")
def resolve_workspace_pipeline_tags(workspace: Workspace, info, **kwargs):
    return list(
        Tag.objects.filter(pipelines__workspace=workspace)
        .distinct()
        .values_list("name", flat=True)
        .order_by("name")
    )


@workspace_object.field("pipelineLastRunStatuses")
def resolve_workspace_pipeline_last_run_statuses(workspace: Workspace, info, **kwargs):
    last_run_state_subquery = (
        PipelineRun.objects.filter(pipeline=OuterRef("pk"))
        .order_by("-execution_date")
        .values("state")[:1]
    )

    states = (
        Pipeline.objects.filter(workspace=workspace, deleted_at__isnull=True)
        .annotate(last_run_status=Subquery(last_run_state_subquery))
        .exclude(last_run_status__isnull=True)
        .values_list("last_run_status", flat=True)
        .distinct()
    )

    return [PipelineRun.STATUS_MAPPINGS.get(state) for state in states if state]


@workspace_object.field("pipelineTemplateTags")
def resolve_workspace_pipeline_template_tags(workspace: Workspace, info, **kwargs):
    if workspace.organization:
        return (
            Tag.objects.filter(
                pipeline_templates__workspace__organization=workspace.organization
            )
            .distinct()
            .values_list("name", flat=True)
            .order_by("name")
        )
    return (
        Tag.objects.filter(pipeline_templates__workspace=workspace)
        .distinct()
        .values_list("name", flat=True)
        .order_by("name")
    )


@workspace_membership_object.field("organizationMembership")
def resolve_workspace_membership_organization_membership(
    membership: WorkspaceMembership, info, **kwargs
):
    """Return the user's organization membership if the workspace belongs to an organization."""
    if not membership.workspace.organization:
        return None

    try:
        return OrganizationMembership.objects.get(
            user=membership.user, organization=membership.workspace.organization
        )
    except OrganizationMembership.DoesNotExist:
        return None


@connection_interface.field("fields")
def resolve_workspace_connection_fields(obj, info, **kwargs):
    return obj.fields.all()


@connection_field_object.field("value")
def resolve_connection_field_value(obj: ConnectionField, info, **kwargs):
    request: HttpRequest = info.context["request"]
    if obj.secret is False:
        return obj.value
    # FIXME this is a temporary solution to allow pipelines to see the secrets
    if (
        isinstance(request.user, PipelineRunUser)
        and request.user.pipeline_run.pipeline.workspace == obj.connection.workspace
    ):
        return obj.value
    if request.user.has_perm("workspaces.update_connection", obj.connection):
        return obj.value


@dhis2_connection.field("queryMetadata")
def resolve_query(connection, info, page=1, per_page=10, filters=None, **kwargs):
    try:
        query_type = DHIS2MetadataQueryType[kwargs["type"]]
        fields = ["id", "name"] + (
            ["level"] if query_type == DHIS2MetadataQueryType.ORG_UNIT_LEVELS else []
        )

        dhis2_client = toolbox_client_from_connection(connection)

        response = query_dhis2_metadata(
            dhis2_client,
            query_type=query_type,
            fields=",".join(fields),
            page=page,
            pageSize=per_page,
            filters=filters,
        )
        result = [
            {
                "label": item.get("name") or item.get("level"),
                "id": item.get("id") or item.get("level"),
            }
            for item in response.items
        ]

        return {
            "items": result,
            "total_items": response.total_items,
            "total_pages": response.total_pages,
            "page_number": response.page_number,
            "success": True,
            "error": None,
        }

    except Exception as e:
        logging.error(f"DHIS2 error: {e}")
        return {
            "items": [],
            "total_items": 0,
            "total_pages": 0,
            "page_number": page,
            "success": False,
            "error": "REQUEST_ERROR"
            if isinstance(e, DHIS2ToolboxError)
            else "UNKNOWN_ERROR",
        }


@iaso_connection.field("queryMetadata")
def resolve_iaso_query(
    connection, info, search=None, page=1, per_page=10, filters=None, **kwargs
):
    try:
        query_type = IASOMetadataQueryType[kwargs["type"]]
        iaso_client = toolbox_client_from_connection(connection)
        params = {}
        # Use tree search to accelerate the search on large IASO instances
        if query_type == IASOMetadataQueryType.IASO_ORG_UNITS:
            params["optimized"] = True

        if filters:
            for filter in filters:
                if filter.get("value"):
                    params[filter["type"]] = filter["value"]
        if search:
            params["search"] = search

        response = query_iaso_metadata(
            iaso_client,
            query_type=query_type,
            page=page,
            limit=per_page,
            **params,
        )

        result = [
            {
                "label": item.get("name"),
                "id": item.get("id"),
            }
            for item in response.items
        ]
        return {
            "items": result,
            "total_items": response.total_items,
            "total_pages": response.total_pages,
            "page_number": response.page_number,
            "success": True,
            "error": None,
        }

    except Exception as e:
        logging.error(f"IASO error: {e}")
        return {
            "items": [],
            "total_items": 0,
            "total_pages": 0,
            "page_number": page,
            "success": False,
            "error": "REQUEST_ERROR" if isinstance(e, IASOError) else "UNKNOWN_ERROR",
        }


connection_interface.set_alias("type", "connection_type")


@dhis2_connection.field("status")
def resolve_dhis2_connection_status(connection, info, **kwargs):
    try:
        toolbox_client_from_connection(connection)
        return "UP"
    except DHIS2ToolboxError as e:
        logging.error(f"DHIS2 error: {e}")
        return "DOWN"
    except Exception as e:
        logging.error(f"Unknown error: {e}")
        return "UNKNOWN"


@connection_interface.type_resolver
def resolve_connection_type(obj, *_):
    connection_type_mapping = {
        "DHIS2": "DHIS2Connection",
        "S3": "S3Connection",
        "POSTGRESQL": "PostgreSQLConnection",
        "CUSTOM": "CustomConnection",
        "GCS": "GCSConnection",
        "IASO": "IASOConnection",
    }
    if isinstance(obj, Connection):
        resolved_type = connection_type_mapping.get(obj.connection_type)
        if resolved_type:
            return resolved_type
        logging.warning(f"Unknown connection type: {obj.connection_type}")
    return None


bindables = [
    workspace_object,
    workspace_permissions,
    workspace_membership_object,
    connection_field_object,
    connection_interface,
    dhis2_connection,
    iaso_connection,
    iaso_metadata_type,
    connection_permissions_object,
    dhis2_metadata_type,
]
