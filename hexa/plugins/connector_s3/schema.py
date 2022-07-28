from ariadne import MutationType, QueryType

from hexa.core.graphql import (
    generate_collections_type_defs_and_bindables,
    load_type_defs_from_file,
)

base_type_defs = load_type_defs_from_file("plugins/connector_s3/graphql/schema.graphql")

query = QueryType()
mutations = MutationType()

# collection extensions
(
    collections_type_defs,
    collections_bindables,
) = generate_collections_type_defs_and_bindables(
    entry_type="S3Object",
)

s3_type_defs = [base_type_defs, collections_type_defs]
s3_bindables = [query, mutations, *collections_bindables]
