import pathlib

from ariadne import (
    EnumType,
    MutationType,
    ObjectType,
    load_schema_from_path,
)
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.workspaces.models import Workspace

from .utils import (
    OrderByDirectionEnum,
    get_database_definition,
    get_table_definition,
    get_table_rows,
    get_table_sample_data,
)

databases_types_def = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

database_object = ObjectType("Database")
database_table_object = ObjectType("DatabaseTable")
workspace_object = ObjectType("Workspace")
workspace_mutations = MutationType()

order_by_direction_enum = EnumType("OrderByDirection", OrderByDirectionEnum)


@database_object.field("tables")
def resolve_database_tables(workspace, info, page=1, per_page=15, **kwargs):
    tables = get_database_definition(
        workspace=workspace,
    )
    return result_page(tables, page=page, per_page=per_page)


@database_object.field("table")
def resolve_database_table(workspace, info, **kwargs):
    return get_table_definition(workspace, kwargs.get("name"))


@database_object.field("credentials")
def resolve_database_credentials(workspace: Workspace, info, **kwargs):
    request: HttpRequest = info.context["request"]
    if request.user.has_perm("databases.view_database_credentials", workspace):
        return {
            "db_name": workspace.db_name,
            "username": workspace.db_name,
            "host": workspace.db_host,
            "port": workspace.db_port,
            "password": workspace.db_password,
            "url": workspace.db_url,
        }
    return None


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


@database_table_object.field("rows")
def resolve_workspace_table_rows(
    table,
    info,
    order_by,
    direction,
    page,
    per_page=15,
):
    results = get_table_rows(
        table["workspace"], table["name"], order_by, direction, page, per_page
    )

    return {
        "page_number": results.page,
        "items": results.items,
        "has_next_page": results.has_next,
        "has_previous_page": results.has_previous,
    }


@workspace_object.field("database")
def resolve_workspace_database(workspace: Workspace, info, **kwargs):
    return workspace


@workspace_mutations.field("generateNewDatabasePassword")
def resolve_generate_new_database_password(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        workspace: Workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=input["workspace_slug"]
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
    workspace_object,
    workspace_mutations,
    order_by_direction_enum,
]
