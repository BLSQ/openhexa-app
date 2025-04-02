import logging

from ariadne import EnumType, InterfaceType, ObjectType
from django.http import HttpRequest
from openhexa.toolbox.dhis2.api import DHIS2Error

from hexa.core.graphql import result_page
from hexa.pipelines.authentication import PipelineRunUser
from hexa.user_management.schema import me_permissions_object

from ..models import (
    Connection,
    ConnectionField,
    Workspace,
    WorkspaceInvitation,
    WorkspaceInvitationStatus,
)
from ..utils import (
    DHIS2MetadataQueryType,
    dhis2_client_from_connection,
    query_dhis2_metadata,
)

workspace_object = ObjectType("Workspace")
workspace_permissions = ObjectType("WorkspacePermissions")
connection_interface = InterfaceType("Connection")
connection_field_object = ObjectType("ConnectionField")
connection_permissions_object = ObjectType("ConnectionPermissions")
dhis2_connection = ObjectType("DHIS2Connection")
dhis2_metadata_type = EnumType("DHIS2MetadataType", DHIS2MetadataQueryType)


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
        request.user.has_perm("workspaces.create_workspace")
        if request.user.is_authenticated
        else False
    )


@workspace_permissions.field("update")
def resolve_workspace_permission_update(workspace: Workspace, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("workspaces.update_workspace", workspace)


@workspace_permissions.field("delete")
def resolve_workspace_permission_delete(workspace: Workspace, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("workspaces.delete_workspace", workspace)


@workspace_permissions.field("manageMembers")
def resolve_workspace_permission_manage(workspace: Workspace, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("workspaces.manage_members", workspace)


@workspace_permissions.field("launchNotebookServer")
def resolve_workspace_permission_launch_notebooks(workspace: Workspace, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("workspaces.launch_notebooks", workspace)


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


@workspace_object.field("members")
def resolve_workspace_members(workspace: Workspace, info, **kwargs):
    qs = workspace.workspacemembership_set.all().order_by("-updated_at")
    return result_page(
        queryset=qs,
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", qs.count()),
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


@workspace_object.field("connections")
def resolve_workspace_connections(workspace: Workspace, info, **kwargs):
    return workspace.connections.all()


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

        dhis2_client = dhis2_client_from_connection(connection)

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
            "error": "REQUEST_ERROR" if isinstance(e, DHIS2Error) else "UNKNOWN_ERROR",
        }


connection_interface.set_alias("type", "connection_type")


@dhis2_connection.field("status")
def resolve_dhis2_connection_status(connection, info, **kwargs):
    try:
        dhis2_client_from_connection(connection)
        return "UP"
    except DHIS2Error as e:
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
    connection_field_object,
    connection_interface,
    dhis2_connection,
    connection_permissions_object,
    dhis2_metadata_type,
]
