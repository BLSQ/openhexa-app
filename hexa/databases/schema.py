import pathlib

from ariadne import ObjectType, convert_kwargs_to_snake_case, load_schema_from_path

from hexa.core.graphql import result_page
from hexa.workspaces.models import Workspace

from .utils import get_database_definition, get_table_definition, get_table_sample_data

databases_types_def = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

database_object = ObjectType("Database")
database_table_object = ObjectType("DatabaseTable")
workspace_object = ObjectType("Workspace")


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


databases_bindables = [database_object, database_table_object, workspace_object]
