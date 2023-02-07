import pathlib

from ariadne import ObjectType, load_schema_from_path

from .utils import get_database_definition, get_table_data, get_table_definition

databases_types_def = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

database_object = ObjectType("Database")
database_table_object = ObjectType("DatabaseTable")


@database_object.field("tables")
def resolve_database_tables(workspace, info, **kwargs):
    return get_database_definition(
        workspace=workspace,
        page=kwargs.get("page", 1),
        per_page=kwargs.get("perPage", 5),
    )


@database_object.field("table")
def resolve_database_table(workspace, info, **kwargs):
    return get_table_definition(workspace, kwargs.get("name"))


@database_table_object.field("sample")
def resolve_database_table_sample(table, info, **kwargs):
    return get_table_data(None, table["name"])


databases_bindables = [database_object, database_table_object]
