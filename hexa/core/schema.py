import pathlib
from uuid import UUID

from ariadne import QueryType, ScalarType, load_schema_from_path

core_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

core_queries = QueryType()

uuid_scalar = ScalarType("UUID")


@uuid_scalar.value_parser
def parse_uuid_value(value):
    try:
        UUID(value, version=4)
        return str(value).upper()
    except (ValueError, TypeError):
        raise ValueError(f'"{value}" is not a valid uuid')


core_bindables = [
    core_queries,
    uuid_scalar,
]
