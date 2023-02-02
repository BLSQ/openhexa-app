import pathlib

from ariadne import ObjectType, QueryType, load_schema_from_path

from hexa.core.graphql import result_page
from hexa.plugins.connector_postgresql.models import Database

from .utils import get_database_tables_summary, get_table_summary

databases_types_def = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

database_object = ObjectType("Database")
database_table_object = ObjectType("DatabaseTable")
database_queries = QueryType()


@database_object.field("tables")
def resolve_database_tables(database, info, **kwargs):
    tables_summary = get_database_tables_summary(database=database)
    paged_tables = result_page(
        queryset=tables_summary,
        page=kwargs.get("page", 1),
        per_page=kwargs.get("perPage", 5),
    )
    return paged_tables


@database_table_object.field("columns")
def resolve_database_table_columns(obj, info):
    try:
        r = get_table_summary(obj["database"], obj["name"])
        return r
    except Exception as e:
        print(f"Exception e {e}", flush=True)
        return []


@database_queries.field("databaseTable")
def resolve_database_table(obj, info, **kwargs):
    try:
        database = Database.objects.get(database=kwargs["databaseId"])
        result = get_database_tables_summary(database, kwargs["id"])
        return result[0] if result else None
    except Database.DoesNotExist:
        return None


databases_bindables = [database_queries, database_object, database_table_object]
