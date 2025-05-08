import pathlib

from ariadne import load_schema_from_path

from .queries import bindables as queries_bindables

search_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.parent.resolve()}/graphql/schema.graphql"
)

search_bindables = queries_bindables
