import pathlib

from ariadne import (
    MutationType,
    ObjectType,
    convert_kwargs_to_snake_case,
    load_schema_from_path,
)
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.workspaces.models import Workspace

from .api import get_db_server_credentials
from .utils import get_database_definition, get_table_definition, get_table_sample_data

databases_types_def = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

database_object = ObjectType("Database")
database_table_object = ObjectType("DatabaseTable")
database_credentials_object = ObjectType("DatabaseCredentials")
workspace_object = ObjectType("Workspace")
workspace_mutations = MutationType()


@database_object.field("tables")
@convert_kwargs_to_snake_case
def resolve_database_tables(workspace, info, page=1, per_page=15, **kwargs):
    tables = get_database_definition(
        workspace=workspace,
    )
    return result_page(tables, page=page, per_page=per_page)


@database_object.field("table")
def resolve_database_table(workspace, info, **kwargs):
    return get_table_definition(workspace, kwargs.get("name"))


@database_object.field("credentials")
def resolve_database_credentials(workspace, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return (
        workspace
        if request.user.has_perm("databases.view_database_credentials", workspace)
        else None
    )


@database_credentials_object.field("port")
def resolve_database_credentials_port(_, info, **kwargs):
    return get_db_server_credentials()["port"]


@database_credentials_object.field("host")
def resolve_database_credentials_host(workspace, info, **kwargs):
    return f"{workspace.slug}.{settings.WORKSPACES_DATABASE_PROXY_HOST}"


@database_credentials_object.field("password")
def resolve_database_credentials_(workspace, info, **kwargs):
    return workspace.db_password


@database_credentials_object.field("url")
def resolve_database_credentials_url(workspace, info, **kwargs):
    host = get_db_server_credentials()["host"]
    port = get_db_server_credentials()["port"]
    return f"postgresql+psycopg2://{workspace.db_name}:{workspace.db_password}@{host}:{port}/{workspace.db_name}"


database_credentials_object.set_alias("dbName", "db_name")
database_credentials_object.set_alias("username", "db_name")


@database_table_object.field("columns")
def resolve_database_table_columns(table, info, **kwargs):
    columns = table.get("columns")
    if columns is None:
        # If we come from database.tables, the table columns are not fetched by default
        columns = get_table_definition(table.get("workspace"), table["name"])["columns"]

    return columns


@database_table_object.field("sample")
def resolve_database_table_sample(table, info, **kwargs):
    return get_table_sample_data(table["workspace"], table["name"])


@workspace_object.field("database")
def resolve_workspace_database(workspace: Workspace, info, **kwargs):
    return workspace


@workspace_mutations.field("generateNewDatabasePassword")
def resolve_generate_new_database_password(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        workspace: Workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=input["workspaceSlug"]
        )

        workspace.generate_new_database_password(principal=request.user)

        return {"success": True, "workspace": workspace, "errors": []}
    except Workspace.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


databases_bindables = [
    database_object,
    database_table_object,
    database_credentials_object,
    workspace_object,
    workspace_mutations,
]
