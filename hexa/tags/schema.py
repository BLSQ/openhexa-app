import pathlib

from ariadne import MutationType, QueryType, load_schema_from_path

tags_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)
tags_query = QueryType()
tags_mutations = MutationType()


tags_bindables = []
