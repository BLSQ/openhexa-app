import pathlib

from ariadne import MutationType, QueryType, load_schema_from_path

s3_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)
s3_query = QueryType()
s3_mutations = MutationType()


s3_bindables = []
