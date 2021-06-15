from ariadne import (
    make_executable_schema,
    snake_case_fallback_resolvers,
)

from hexa.catalog.schema import catalog_type_defs, catalog_bindables
from hexa.user_management.schema import identity_type_defs, identity_bindables

type_defs = """
    scalar Date
    scalar DateTime
    
    type Query
    type Mutation
"""

schema = make_executable_schema(
    [type_defs, catalog_type_defs, identity_type_defs],
    [*catalog_bindables, *identity_bindables, snake_case_fallback_resolvers],
)
