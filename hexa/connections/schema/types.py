import logging

from ariadne import InterfaceType, ObjectType
from django.http import HttpRequest
from openhexa.toolbox.dhis2.api import DHIS2Error

from hexa.connections.dhis2_client_helper import query_dhis2_metadata
from hexa.pipelines.authentication import PipelineRunUser
from hexa.workspaces.models import Connection, ConnectionField

dhis2_connection = ObjectType("DHIS2Connection")
connection_object = InterfaceType("Connection")
connection_field_object = ObjectType("ConnectionField")
connection_permissions_object = ObjectType("ConnectionPermissions")


@dhis2_connection.field("metadataQuery")
def resolve_query(dhis2_client, info, **kwargs):
    fields = ["id", "name"]

    try:
        metadata = query_dhis2_metadata(
            dhis2_client,
            type=kwargs.get("type"),
            fields=fields,
            filter=kwargs.get("filter"),
        )

        result = [{field: item.get(field) for field in fields} for item in metadata]
        return {"data": result, "success": True, "errors": []}
    except DHIS2Error as e:
        logging.error(f"DHIS2 error: {e}")
        return {"data": [], "success": False, "errors": ["CONNECTION_ERROR"]}
    except Exception as e:
        logging.error(f"Unknown error: {e}")
        return {"data": [], "success": False, "errors": ["UNKNOWN_ERROR"]}


@connection_object.field("permissions")
def resolve_workspace_connection_permissions(connection: Connection, info):
    return connection


@connection_permissions_object.field("update")
def resolve_connection_permissions_update(connection: Connection, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("workspaces.update_connection", connection)


@connection_permissions_object.field("delete")
def resolve_connection_permissions_delete(connection: Connection, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("workspaces.delete_connection", connection)


@connection_object.field("fields")
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


connection_object.set_alias("type", "connection_type")

bindables = [
    dhis2_connection,
    connection_field_object,
    connection_object,
    connection_permissions_object,
]
