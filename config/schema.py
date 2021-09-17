from ariadne import make_executable_schema, snake_case_fallback_resolvers

from hexa.catalog.schema import catalog_bindables, catalog_type_defs
from hexa.plugins.connector_dhis2.schema import dhis2_bindables, dhis2_type_defs
from hexa.plugins.connector_s3.schema import s3_bindables, s3_type_defs
from hexa.user_management.schema import identity_bindables, identity_type_defs

type_defs = """
    scalar Date
    scalar DateTime
    
    type Query
    type Mutation
"""

schema = make_executable_schema(
    [type_defs, catalog_type_defs, identity_type_defs, dhis2_type_defs, s3_type_defs],
    [
        *catalog_bindables,
        *identity_bindables,
        *dhis2_bindables,
        *s3_bindables,
        snake_case_fallback_resolvers,
    ],
)
